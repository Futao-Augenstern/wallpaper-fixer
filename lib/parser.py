"""
Wallpaper Engine 诊断文件解析器
---------------------------------
解析 Wallpaper Engine 导出的 info.txt（以及由它生成的 markdown 报告），
抽取关键故障信号并输出结构化 findings，供前端展示与修复模块使用。

设计原则：
- 纯文本启发式解析，不依赖固定格式，缺字段也不报错。
- 每条 finding 自带 severity / evidence / recommendation / fix_actions，
  前端与修复模块直接消费。
- 正则统一在模块加载时预编译（RE_* 常量），避免每次调用重复编译。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional

# 严重级别排序（数值越小越靠前）
SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2, "ok": 3}

# CEF / Assimp 相关 DLL 前缀，用于依赖缺失分类
_CEF_PREFIXES = ("chrome_elf", "libcef", "libegl", "libglesv2", "cef")

# 预编译正则：所有检测共用，避免每次解析重复编译
RE_DXGI_LOST = re.compile(r"DXGI\s+device\s+lost", re.IGNORECASE)
RE_DXGI_INIT = re.compile(r"DXGI\s+failed\s+init\s*:\s*([0-9a-fx]+)", re.IGNORECASE)
RE_DXGI_CTX = re.compile(
    r".{0,40}DXGI\s+(device lost|failed init|begin recovery|finish recovery).{0,40}", re.IGNORECASE)
RE_DEPS_X86 = re.compile(
    r"deps errors x86\s*:(.*?)(?:\n\s*\n|deps errors x64|Dependency error analysis|$)",
    re.IGNORECASE | re.DOTALL)
RE_LOADED0 = re.compile(r".{0,60}loaded:\s*0.{0,20}", re.IGNORECASE)
RE_DLL = re.compile(r"([\w\-\.]+\.dll)", re.IGNORECASE)
RE_TRAY = re.compile(r"icon create err\s*:\s*(-?\d+)", re.IGNORECASE)
RE_JS = re.compile(
    r"(Uncaught\s+\w+Error\s*:[^\n]+|JS Exception\s*:[^\n]+|window\.\w+ is not a function)",
    re.IGNORECASE)
RE_GPU_LINE = re.compile(
    r"(NVIDIA[^\n]{0,50}|Intel[^\n]{0,50}Graphics[^\n]{0,30}|Radeon[^\n]{0,40})", re.IGNORECASE)

# 元信息提取正则
RE_META = {
    "we_version": re.compile(r"Wallpaper\s*Engine[^\d]*v?(\d+\.\d+\.\d+)"),
    "windows": re.compile(r"Windows\s*(1[01])[^\n]*?(?:Build\s*(\d+))?"),
    "os_caption": re.compile(r"Caption\s*[:=]\s*(Windows[^\n]+)"),
    "gpu": re.compile(r"(NVIDIA|Intel|AMD|Radeon|GeForce)[^\n]{0,60}"),
}


@dataclass
class Finding:
    id: str
    severity: str          # critical | warning | info | ok
    title: str
    detail: str = ""
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    fix_actions: list[str] = field(default_factory=list)
    count: Optional[int] = None


@dataclass
class DiagnosticResult:
    source: str
    meta: dict
    findings: list[Finding]
    summary: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["findings"].sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
        return d


# ---------------------------------------------------------------------------
# 元信息提取
# ---------------------------------------------------------------------------

def _extract_meta(text: str) -> dict:
    meta: dict = {}
    for key, pat in RE_META.items():
        m = pat.search(text)
        if m:
            meta[key] = " ".join(g for g in m.groups() if g).strip()
    gpus: set[str] = set()
    for m in RE_GPU_LINE.finditer(text):
        gpus.add(m.group(1).strip())
    if gpus:
        meta["gpu_detected"] = list(gpus)
    return meta


# ---------------------------------------------------------------------------
# 各项检测（每个函数职责单一：只负责一类信号）
# ---------------------------------------------------------------------------

def _detect_dxgi(text: str) -> Optional[Finding]:
    lost = len(RE_DXGI_LOST.findall(text))
    failed_init = RE_DXGI_INIT.findall(text)
    if lost == 0 and not failed_init:
        return None
    code = failed_init[0] if failed_init else None
    ev = RE_DXGI_CTX.findall(text)
    detail = (
        f"日志中出现 {lost} 次 “DXGI device lost”，"
        f"{len(failed_init)} 次初始化失败"
        + (f"（错误码 {code}）" if code else "")
        + "。典型的“丢失 → 恢复 → 再丢失”死循环，指向显卡驱动与系统图形栈契约断裂。"
    )
    rec = (
        "优先：① 用 DDU 在安全模式清洁重装 NVIDIA/Intel 驱动；"
        "② 强制壁纸引擎走独显；③ 关闭硬件加速 GPU 调度(HAGS)；"
        "④ 双显卡机型检查显卡切换。"
    )
    return Finding(
        id="dxgi_device_lost",
        severity="critical",
        title="GPU 渲染反复崩溃（DXGI 设备丢失）",
        detail=detail,
        evidence=ev[:8],
        recommendation=rec,
        fix_actions=["set_dgpu", "disable_hags", "reinstall_driver", "run_dism"],
        count=lost,
    )


def _detect_deps(text: str) -> Optional[Finding]:
    missing: list[str] = []
    m = RE_DEPS_X86.search(text)
    if m:
        for line in m.group(1).splitlines():
            if "loaded: 0" in line or "Error module" in line:
                name = RE_DLL.search(line)
                if name:
                    missing.append(name.group(1))
    # 兜底：全文扫描 loaded: 0 的 dll
    for line in RE_LOADED0.findall(text):
        nm = RE_DLL.search(line)
        if nm and nm.group(1) not in missing:
            missing.append(nm.group(1))
    if not missing:
        return None
    cef = [d for d in missing if d.lower().startswith(_CEF_PREFIXES)]
    assimp = [d for d in missing if "assimp" in d.lower()]
    detail = (
        f"检测到 {len(missing)} 个 32 位依赖无法加载：{', '.join(missing)}。"
        + (" 其中 CEF/Chromium 组件缺失会导致 Web/HTML 壁纸不可用；" if cef else "")
        + (" Assimp 缺失会影响 3D/Scene 壁纸导入。" if assimp else "")
    )
    rec = (
        "最常见原因是安装损坏（更新失败/被杀软拦截）。先做 Steam → 库 → Wallpaper Engine → "
        "属性 → 已安装文件 → 验证游戏文件的完整性，通常可补全缺失 DLL。"
    )
    return Finding(
        id="deps_missing_x86",
        severity="warning",
        title="32 位依赖缺失（CEF / Assimp 等 loaded:0）",
        detail=detail,
        evidence=[f"loaded: 0 -> {d}" for d in missing[:8]],
        recommendation=rec,
        fix_actions=["verify_steam_files"],
        count=len(missing),
    )


def _detect_tray(text: str) -> Optional[Finding]:
    errs = RE_TRAY.findall(text)
    if not errs:
        return None
    last = errs[-1]
    hexcode = f"0x{int(last) & 0xFFFFFFFF:08X}"
    detail = (
        f"出现 {len(errs)} 次托盘图标创建失败（{last} = {hexcode} = E_FAIL）。"
        "通常由第三方外壳增强（Winstep / Windhawk 等注入 explorer 的模块）干扰 Shell 托盘导致，"
        "不影响壁纸渲染，但会导致引擎托盘图标/右键菜单偶发异常。"
    )
    rec = "排查第三方外壳程序：临时退出 Winstep Xtreme、Windhawk，或用 msconfig 干净启动后观察是否消失。"
    return Finding(
        id="tray_icon_fail",
        severity="info",
        title="系统托盘图标创建失败（E_FAIL）",
        detail=detail,
        evidence=[f"icon create err: {e}" for e in errs[:5]],
        recommendation=rec,
        fix_actions=["detect_conflicts"],
        count=len(errs),
    )


def _detect_web_script(text: str) -> Optional[Finding]:
    js = RE_JS.findall(text)
    if not js:
        return None
    detail = (
        f"检测到 {len(js)} 条 Web/HTML 壁纸脚本报错。多数属于个别壁纸自身脚本缺陷"
        "（在引擎注入 scene API 之前就执行），非引擎本体问题；少数可能源于 CEF 组件异常。"
    )
    rec = "若是固定某张壁纸触发，换用其他壁纸即可；若多张 Web 壁纸都报错，优先修复上面的 CEF 依赖缺失。"
    return Finding(
        id="web_script_error",
        severity="info",
        title="Web/HTML 壁纸脚本报错",
        detail=detail,
        evidence=[j.strip()[:120] for j in js[:6]],
        recommendation=rec,
        fix_actions=["verify_steam_files"],
        count=len(js),
    )


def _detect_cef_ui(text: str) -> Optional[Finding]:
    markers = ("CefStreamReader::CreateForFile failed", "updateProfileCallback is not a function")
    if any(mk in text for mk in markers):
        return Finding(
            id="cef_ui_glitch",
            severity="info",
            title="UI 层 CEF 偶发毛刺",
            detail="引擎 UI 在加载本地资源/回调时偶发失败，属 UI 偶发毛刺，优先级最低。",
            evidence=["LocalFileSchemeFactory: CefStreamReader::CreateForFile failed",
                      "JS Exception: Uncaught TypeError: window.updateProfileCallback is not a function"],
            recommendation="一般不影响使用；若频繁出现可随 CEF 依赖修复一并解决。",
            fix_actions=["verify_steam_files"],
        )
    return None


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def parse_diagnostic(text: str, source: str = "upload") -> DiagnosticResult:
    text = text or ""
    meta = _extract_meta(text)
    findings: list[Finding] = []
    for fn in (_detect_dxgi, _detect_deps, _detect_tray, _detect_web_script, _detect_cef_ui):
        f = fn(text)
        if f:
            findings.append(f)

    if not findings:
        findings.append(Finding(
            id="no_issue",
            severity="ok",
            title="未检测到已知故障模式",
            detail="在当前文本中未发现 DXGI 崩溃、依赖缺失、托盘错误或脚本异常等典型信号。",
            recommendation="若仍有问题，请确认导出的诊断信息完整，或描述具体现象。",
        ))

    critical = [f for f in findings if f.severity == "critical"]
    warning = [f for f in findings if f.severity == "warning"]
    if critical:
        summary = "存在严重的 GPU 渲染崩溃，需优先处理显卡驱动与双显卡设置。"
    elif warning:
        summary = "存在依赖缺失等可修复问题，建议先验证游戏文件完整性。"
    else:
        summary = "未发现严重问题。"

    return DiagnosticResult(source=source, meta=meta, findings=findings, summary=summary)


def parse_file(path: str) -> DiagnosticResult:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return parse_diagnostic(fh.read(), source=path)
