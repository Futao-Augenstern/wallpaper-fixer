"""
实时系统体检模块
----------------
通过 PowerShell / WMI 读取当前机器的真实状态，供前端“系统体检”展示，
并为修复模块判定前置条件。

设计要点（深度优化）：
- 原先串行启动 6 个 powershell.exe 进程，慢且占资源；现合并为 **1 次调用**，
  由一段 PowerShell 脚本返回单个 JSON，再由纯函数 _parse_scan 解析。
- 解析逻辑与“执行 PS”解耦：_parse_scan(raw_json) 是纯函数，便于单元测试，
  也不需要 Windows 即可测。
- 结果带 10s TTL 缓存：短时间内重复体检直接返回缓存，避免无谓的 PowerShell 开销；
  同时保留并发锁，防止缓存未命中时多个体检并行堆积进程。
- 单个子检查在 PowerShell 内已 try/catch，整体仍对局部失败健壮。

本模块只在 Windows 上有效；非 Windows 返回 platform_unsupported。
"""

from __future__ import annotations

import json
import platform
import subprocess
import threading
import time

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
PS_TIMEOUT_SYSTEM = 30           # 合并体检单次调用超时（含事件日志查询）

# HAGS 注册表值：1=开启，2=关闭
HAGS_ENABLED = 1
HAGS_DISABLED = 2

# 缓存与并发
_CACHE_TTL = 10                  # 秒；短时间内重复体检直接命中缓存
_cache: dict = {"ts": 0.0, "data": None}
_cache_lock = threading.Lock()
_scan_lock = threading.Lock()    # 同一时刻只允许一个真实体检在跑

# 进程名白名单（用于冲突识别与运行态展示）
_WANT_PROCS = (
    "wallpaper64", "wallpaper32", "wallpaperservice64", "wallpaperservice32",
    "windhawk", "wsxcfg", "wsxservice", "nvcontainer",
)


# ---------------------------------------------------------------------------
# 单进程 PowerShell 调用
# ---------------------------------------------------------------------------

def _run_ps(script: str, timeout: int = PS_TIMEOUT_SYSTEM) -> str:
    """运行一段 PowerShell 脚本，返回 stdout 文本。异常向上抛。"""
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip() or f"powershell exit {proc.returncode}")
    return proc.stdout


# 合并体检脚本：一次返回所有子项的 JSON（各段内部已 try/catch）
_SYSTEM_SCAN_SCRIPT = r"""
$errs = @()
function Safe($n, $c) { try { & $c } catch { $global:errs += ($n + ': ' + $_.Exception.Message); $null } }

$os = Safe os { Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture }
$gpus = @(Safe gpus { Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, Status, VideoProcessor, AdapterRAM })
$hags = Safe hags {
    $h = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'
    if (Test-Path $h) {
        $v = Get-ItemProperty -Path $h -Name HwSchMode -ErrorAction SilentlyContinue
        if ($v) { [int]$v.HwSchMode } else { 'unknown' }
    } else { 'unknown' }
}
$procs = @(Safe procs { Get-Process | Select-Object Name, Id })

$we = Safe we {
    $wp = $null
    $p = (Get-Process wallpaper64 -ErrorAction SilentlyContinue | Select-Object -First 1).Path
    if ($p) { $wp = (Get-Item $p).DirectoryName }
    if (-not $wp) {
        foreach ($c in @('C:\Program Files (x86)\Steam\steamapps\common\Wallpaper Engine',
                          'C:\Program Files\Steam\steamapps\common\Wallpaper Engine')) {
            if (Test-Path $c) { $wp = $c; break }
        }
    }
    $missing = @(); $w32 = $null
    if ($wp) {
        foreach ($d in @('wallpaper32.exe', 'libcef.dll', 'assimp-vc140-mt32.dll',
                          'chrome_elf.dll', 'libegl.dll', 'libglesv2.dll')) {
            $e = Test-Path (Join-Path $wp $d)
            if ($d -eq 'wallpaper32.exe') { $w32 = $e }
            elseif ($e -eq $false) { $missing += $d }
        }
    }
    [ordered]@{ path = $wp; missing = $missing; w32 = $w32 }
}
$dxgi = Safe dxgi {
    [int](Get-WinEvent -FilterHashtable @{ LogName = 'System'; Level = 2;
            ProviderName = 'Display', 'nvlddmkm', 'igfx', 'dxgkrnl' } `
        -MaxEvents 50 -ErrorAction SilentlyContinue |
        Measure-Object | Select-Object -ExpandProperty Count)
}

$result = [ordered]@{
    os                = $os
    gpus              = $gpus
    hags              = $hags
    procs             = $procs
    we_path           = $(if ($we) { $we.path } else { $null })
    missing_dlls      = $(if ($we) { $we.missing } else { @() })
    wallpaper32_present = $(if ($we) { $we.w32 } else { $null })
    dxgi_events       = $dxgi
    errors            = $errs
}
$result | ConvertTo-Json -Compress -Depth 4
"""


# ---------------------------------------------------------------------------
# 纯解析函数（无副作用，便于测试）
# ---------------------------------------------------------------------------

def _format_hags(hags_raw):
    if hags_raw in (HAGS_ENABLED, HAGS_DISABLED):
        mode = int(hags_raw)
        return {"value": mode, "enabled": mode == HAGS_ENABLED,
                "note": "开启" if mode == HAGS_ENABLED else "关闭"}
    return {"value": "unknown", "enabled": None,
            "note": "注册表无 HwSchMode（使用系统默认，通常等同于开启）"}


def _build_running(procs) -> dict:
    found: dict = {}
    if not isinstance(procs, list):
        procs = [procs]
    for p in procs:
        if not isinstance(p, dict):
            continue
        nm = (p.get("Name") or "").lower()
        for w in _WANT_PROCS:
            if nm == w or nm.startswith(w):
                found.setdefault(w, []).append(p.get("Id"))
    return found


def _build_we(path, missing, w32) -> dict:
    return {"installed": path is not None, "path": path,
            "missing_x86_dlls": list(missing) if missing else [],
            "wallpaper32_present": w32}


def _build_conflicts(running) -> list:
    conflicts = []
    if running.get("windhawk"):
        conflicts.append("Windhawk（注入 explorer 的外壳增强）")
    if running.get("wsxservice") or running.get("wsxcfg"):
        conflicts.append("Winstep Xtreme（WsxService）")
    return conflicts


def _build_dual(gpus) -> bool:
    names = [(g.get("Name") or "") for g in gpus if isinstance(g, dict)]
    return sum(any(k in (n.lower()) for k in ("intel", "nvidia", "amd", "radeon"))
               for n in names) >= 2


def _error_result(msg: str) -> dict:
    return {
        "os": None, "gpus": [], "hags": _format_hags(None),
        "processes": {},
        "wallpaper_engine": {"installed": False, "path": None,
                             "missing_x86_dlls": [], "wallpaper32_present": None},
        "dxgi_event_errors": None, "conflicts": [], "dual_gpu": False,
        "errors": [msg],
    }


def _parse_scan(raw: str) -> dict:
    """把 PowerShell 返回的 JSON 字符串解析成标准体检结果（纯函数）。"""
    try:
        data = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        return _error_result(f"系统体检输出解析失败: {e}")

    os_info = data.get("os") if isinstance(data.get("os"), dict) else None

    gpus = data.get("gpus") or []
    if not isinstance(gpus, list):
        gpus = [gpus]
    gpus = [g for g in gpus if isinstance(g, dict)]

    hags = _format_hags(data.get("hags"))

    running = _build_running(data.get("procs"))
    we = _build_we(data.get("we_path"), data.get("missing_dlls"),
                   data.get("wallpaper32_present"))

    dxgi = data.get("dxgi_events")
    try:
        dxgi = int(dxgi) if dxgi is not None else None
    except (TypeError, ValueError):
        dxgi = None

    conflicts = _build_conflicts(running)
    dual = _build_dual(gpus)
    errors = data.get("errors") or []

    return {
        "os": os_info,
        "gpus": gpus,
        "hags": hags,
        "processes": running,
        "wallpaper_engine": we,
        "dxgi_event_errors": dxgi,
        "conflicts": conflicts,
        "dual_gpu": dual,
        "errors": errors,
    }


def _collect_once() -> dict:
    try:
        raw = _run_ps(_SYSTEM_SCAN_SCRIPT, timeout=PS_TIMEOUT_SYSTEM)
    except Exception as e:  # noqa: BLE001
        return _error_result(f"系统体检执行失败: {type(e).__name__}: {e}")
    return _parse_scan(raw)


# ---------------------------------------------------------------------------
# 对外入口：非 Windows 短路 + 缓存 + 并发锁
# ---------------------------------------------------------------------------

def collect_system_info() -> dict:
    if platform.system().lower() != "windows":
        return {"platform_unsupported": True,
                "platform": platform.system(),
                "message": "系统体检仅支持 Windows。请在 Windows 上运行本工具。"}

    # 1) 命中缓存直接返回（最快路径）
    with _cache_lock:
        if _cache["data"] is not None and (time.time() - _cache["ts"]) < _CACHE_TTL:
            return _cache["data"]

    # 2) 已有体检在跑：若有缓存则返回（即便略旧），否则返回 busy
    if not _scan_lock.acquire(blocking=False):
        with _cache_lock:
            if _cache["data"] is not None:
                return _cache["data"]
        return {"busy": True, "message": "系统体检正在进行中，请稍候再试。"}

    try:
        data = _collect_once()
        with _cache_lock:
            _cache["ts"] = time.time()
            _cache["data"] = data
        return data
    finally:
        _scan_lock.release()


if __name__ == "__main__":
    print(json.dumps(collect_system_info(), indent=2, ensure_ascii=False))
