"""
一键修复模块
------------
定义各项修复动作并安全执行。安全守则：
- 任何“改动系统”的动作都必须显式 confirm=True 才执行。
- 需要管理员权限的动作，在非管理员下直接返回 needs_admin，由前端提示用户以管理员身份运行。
- SFC / DISM 等耗时操作改为后台执行并写日志，前端轮询日志，避免阻塞请求。
- guided 类动作不改动系统，只打开对应设置页/网页并给出操作指引。

动作 id 与 parser 中 Finding.fix_actions 一一对应。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
import ctypes

LOG_DIR = os.path.join(tempfile.gettempdir(), "wallpaper_fixer_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 命名常量：替代散落的魔法数字
GPU_PREFERENCE_HIGH = 2          # 注册表 UserGpuPreferences 中的“高性能”
HAGS_DISABLED = 2                # 注册表 HwSchMode 关闭值
DETACHED_PROCESS = 0x00000008    # 后台进程脱离父进程
PS_TIMEOUT_QUICK = 20            # 快速查询（解析 exe 路径等）
PS_TIMEOUT_DIRECT = 60           # 直接执行的修复（一般几分钟上限）
PS_TIMEOUT_RESOLVE = PS_TIMEOUT_QUICK

# 修复动作 id 白名单：仅允许小写字母与下划线，杜绝路径穿越等注入
_ACTION_ID_RE = re.compile(r"^[a-z_]+$")


def is_known_action(action_id) -> bool:
    """校验 action id 合法且存在于注册表，防止 /api/fix/log 等接口被滥用读任意文件。"""
    return isinstance(action_id, str) and bool(_ACTION_ID_RE.match(action_id)) \
        and action_id in FIX_ACTIONS


def _ps_str(value: str) -> str:
    """转义 PowerShell 单引号字符串中的单引号，避免命令注入 / 语法错误。"""
    return str(value).replace("'", "''")


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _resolve_we_exe() -> str | None:
    try:
        out = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
             "$p=(Get-Process wallpaper64 -ErrorAction SilentlyContinue | Select-Object -First 1).Path; "
             "if($p){$p}else{$c='C:\\Program Files (x86)\\Steam\\steamapps\\common\\Wallpaper Engine\\wallpaper64.exe'; "
             "if(Test-Path $c){$c}else{''}}"],
            capture_output=True, text=True, timeout=PS_TIMEOUT_RESOLVE, encoding="utf-8", errors="ignore",
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def _run_direct(script: str, timeout: int = PS_TIMEOUT_DIRECT) -> dict:
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="ignore",
    )
    return {"ok": proc.returncode == 0, "rc": proc.returncode,
            "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}


def _run_background(script: str, action_id: str) -> dict:
    log_path = os.path.join(LOG_DIR, f"{action_id}.log")
    # 用 PowerShell 把输出重定向到日志，自身 detached 运行
    wrapper = (
        f"Start-Transcript -Path '{log_path}' -Force; "
        f"try {{ {script} }} catch {{ Write-Output ('ERROR: ' + $_.Exception.Message) }}; "
        f"Write-Output ('__WF_DONE__ ' + (Get-Date)); Stop-Transcript"
    )
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", wrapper],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=DETACHED_PROCESS,  # 后台脱离父进程独立运行
    )
    return {"ok": True, "async": True, "log": log_path,
            "message": "已在后台启动，请稍候并在下方查看进度。"}


# ---------------------------------------------------------------------------
# 动作定义
# ---------------------------------------------------------------------------

FIX_ACTIONS = {
    "set_dgpu": {
        "title": "强制壁纸引擎走独显（高性能 GPU）",
        "description": "在注册表 DirectX UserGpuPreferences 中为 wallpaper64.exe 写入 GpuPreference=2（高性能），"
                       "避免双显卡机型把壁纸引擎分配到核显导致 DXGI 设备丢失。",
        "kind": "mutate", "needs_admin": False, "risk": "低",
        "build": lambda p: (
            f"$exe='{_ps_str(p['exe'])}'; "
            f"$key='HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences'; "
            f"if(-not(Test-Path $key)){{New-Item -Path $key -Force|Out-Null}}; "
            f"New-ItemProperty -Path $key -Name $exe -Value 'GpuPreference={GPU_PREFERENCE_HIGH};' "
            f"-PropertyType String -Force|Out-Null; "
            f"\"set $exe -> high performance\""
        ),
        "params": lambda: {"exe": _resolve_we_exe() or ""},
    },
    "disable_hags": {
        "title": "关闭硬件加速 GPU 调度（HAGS）",
        "description": "将 GraphicsDrivers\\HwSchMode 设为 2（关闭）。该设置与 NVIDIA Blackwell + Win11 25H2 的 "
                       "DXGI 崩溃高度相关，关闭后常可显著减少设备丢失。需重启生效。需要管理员权限。",
        "kind": "mutate", "needs_admin": True, "risk": "低",
        "build": lambda p: (
            "$key='HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers'; "
            f"Set-ItemProperty -Path $key -Name HwSchMode -Value {HAGS_DISABLED} -Type DWord -Force; "
            f"\"HAGS set to disabled ({HAGS_DISABLED})\""
        ),
        "params": lambda: {},
    },
    "run_sfc": {
        "title": "运行 sfc /scannow 修复系统文件",
        "description": "扫描并修复可能损坏的系统文件（含 DirectX/DXGI 相关）。耗时较长（数分钟），后台执行。需要管理员权限。",
        "kind": "mutate_long", "needs_admin": True, "risk": "低",
        "build": lambda p: "sfc /scannow",
        "params": lambda: {},
    },
    "run_dism": {
        "title": "运行 DISM 修复系统映像",
        "description": "在线修复 Windows 组件存储（/RestoreHealth）。耗时较长，后台执行。需要管理员权限。",
        "kind": "mutate_long", "needs_admin": True, "risk": "低",
        "build": lambda p: "DISM /Online /Cleanup-Image /RestoreHealth",
        "params": lambda: {},
    },
    "verify_steam_files": {
        "title": "验证 Wallpaper Engine 游戏文件完整性",
        "description": "打开 Steam 并跳转到 Wallpaper Engine（appid 431960）详情页，请手动点击"
                       "“属性 → 已安装文件 → 验证游戏文件的完整性”，以补全缺失的 32 位 CEF/Assimp 依赖。",
        "kind": "guided", "needs_admin": False, "risk": "无",
        "build": lambda p: "Start-Process 'steam://nav/games/details/431960'; \"已尝试打开 Steam\"",
        "params": lambda: {},
    },
    "detect_conflicts": {
        "title": "排查第三方外壳干扰（Windhawk / Winstep）",
        "description": "列出当前检测到的可能干扰 Shell 托盘/图形栈的第三方程序，并给出临时退出或干净启动的建议。"
                       "本动作不自动结束任何进程。",
        "kind": "guided", "needs_admin": False, "risk": "无",
        "build": lambda p: (
            "Write-Output '请临时退出/卸载 Winstep Xtreme 与 Windhawk，或用 msconfig 干净启动后测试。'"
        ),
        "params": lambda: {},
    },
    "reinstall_driver": {
        "title": "引导显卡驱动清洁重装",
        "description": "打开 NVIDIA 官方驱动下载页与 DDU 说明。建议用 DDU 在安全模式彻底卸载 NVIDIA+Intel 驱动后清洁重装。",
        "kind": "guided", "needs_admin": False, "risk": "无",
        "build": lambda p: (
            "Start-Process 'https://www.nvidia.com/Download/index.aspx'; "
            "Start-Process 'https://www.guru3d.com/download/display-driver-uninstaller-download/'; "
            "\"已打开驱动下载与 DDU 页面\""
        ),
        "params": lambda: {},
    },
    "open_graphics_settings": {
        "title": "打开 Windows 图形设置（手动指定 GPU）",
        "description": "打开“设置 → 系统 → 显示 → 图形”，可手动为 wallpaper64.exe 指定“高性能”。",
        "kind": "guided", "needs_admin": False, "risk": "无",
        "build": lambda p: "Start-Process 'ms-settings:display-advancedgraphics'; \"已打开图形设置\"",
        "params": lambda: {},
    },
}


# ---------------------------------------------------------------------------
# 执行入口
# ---------------------------------------------------------------------------

def run_fix(action_id: str, confirm: bool, params: dict | None = None) -> dict:
    if action_id not in FIX_ACTIONS:
        return {"ok": False, "error": f"未知修复动作: {action_id}"}
    action = FIX_ACTIONS[action_id]
    if not confirm:
        return {"ok": False, "need_confirm": True,
                "title": action["title"], "risk": action["risk"],
                "description": action["description"]}

    # 需要管理员但未提权
    if action["needs_admin"] and not is_admin():
        return {"ok": False, "needs_admin": True,
                "message": "此操作需要管理员权限。请右键“以管理员身份运行”本程序后重试。"}

    try:
        resolved = action["params"]() if callable(action.get("params")) else {}
        if params:
            resolved.update(params)
        # set_dgpu 必须有 exe 路径
        if action_id == "set_dgpu" and not resolved.get("exe"):
            return {"ok": False, "error": "未定位到 wallpaper64.exe，无法设置 GPU 偏好。请确认 Wallpaper Engine 正在运行。"}
        script = action["build"](resolved)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"准备修复脚本失败: {e}"}

    if action["kind"] == "guided":
        # 引导类：只打开对应设置页/网页并给指引，不改动系统。
        # 返回 guided 标记与说明，前端据此展示引导文案而非“执行完成”，且不触发重新体检。
        res = _run_direct(script)
        if not res["ok"]:
            return {"ok": False, "error": res.get("stderr") or res.get("stdout") or "引导步骤执行失败"}
        return {"ok": True, "guided": True,
                "message": res["stdout"] or action["description"]}

    if action["kind"] == "mutate_long":
        # 并发防护：同一耗时任务已有实例在跑则直接返回 busy，避免重复执行 sfc/DISM
        prev = get_fix_log(action_id)
        if prev.get("exists") and not prev.get("done"):
            return {"ok": False, "busy": True,
                    "message": "该修复任务正在进行中，请在日志中查看进度，勿重复触发。"}
        return _run_background(script, action_id)
    return _run_direct(script)


def get_fix_log(action_id: str) -> dict:
    if not is_known_action(action_id):
        return {"exists": False, "done": False, "lines": [], "error": "invalid action"}
    log_path = os.path.join(LOG_DIR, f"{action_id}.log")
    if not os.path.exists(log_path):
        return {"exists": False, "done": False, "lines": []}
    with open(log_path, "r", encoding="utf-8", errors="ignore") as fh:
        lines = fh.read().splitlines()
    done = any("__WF_DONE__" in ln for ln in lines)
    # 去掉 transcript 噪声行
    clean = [ln for ln in lines if ln.strip()
             and "Transcript started" not in ln and "Transcript stopped" not in ln]
    return {"exists": True, "done": done, "lines": clean[-200:]}


def list_actions() -> list[dict]:
    return [{"id": k, **{kk: vv for kk, vv in v.items() if kk not in ("build", "params")}}
            for k, v in FIX_ACTIONS.items()]
