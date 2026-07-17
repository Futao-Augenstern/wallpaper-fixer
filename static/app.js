"use strict";

const $ = (id) => document.getElementById(id);

/* ============================================================
   国际化（中 / 英）
   静态文本走 [data-i18n]；后端返回内容（诊断结论/修复项/体检）
   按 id 在 FIX_I18N / FIND_I18N 中提供英译。
   ============================================================ */
const I18N = {
  zh: {
    app_title: "Wallpaper 修复助手",
    brand_name: "Wallpaper 修复助手",
    brand_sub: "本地诊断 · 系统体检 · 一键修复",
    brand_aria: "Wallpaper 修复助手 首页",
    nav_diag: "诊断分析", nav_scan: "系统体检", nav_fix: "一键修复",
    nav_open: "打开导航菜单", nav_close: "关闭导航菜单",
    btn_scan: "系统体检",
    hero_title: "让壁纸重新动起来",
    hero_sub: "本地运行的 Wallpaper Engine 故障排查工具。上传诊断文件、查看本机图形状态、按需执行修复——全程不联网、不上传任何数据。",
    hero_pill1: "① 分析诊断文件", hero_pill2: "② 实时系统体检", hero_pill3: "③ 一键修复",
    hero_note: "提示：需要修复驱动或系统文件时，请右键本应用以<b>管理员身份运行</b>。",
    card1_title: "① 诊断文件分析", tag_diag: "诊断",
    hint_diag: "上传 Wallpaper Engine 导出的 info.txt，或将诊断文本粘贴到下方，自动识别 DXGI 崩溃 / 依赖缺失 / 托盘错误等问题。",
    file_choose: "选择 info.txt",
    file_aria: "选择诊断文件 info.txt（支持 .txt/.log/.md）",
    filebox_aria: "选择诊断文件 info.txt",
    btn_parse: "解析诊断文件", btn_sample: "载入示例",
    ph_diag: "或直接粘贴诊断文本…",
    card2_title: "② 实时系统体检", tag_scan: "体检",
    hint_scan: "读取本机真实状态：显卡与驱动、双显卡、HAGS 开关、运行进程、冲突软件、事件日志中的显示错误。",
    scan_placeholder: "点击右上角“系统体检”或下方按钮开始。",
    btn_scan2: "开始系统体检",
    card3_title: "③ 一键修复", tag_fix: "修复",
    hint_fix: "以下动作均会二次确认；涉及驱动/系统文件的动作需要管理员权限。耗时操作在后台执行并实时显示日志。",
    loading: "加载中…",
    btn_cancel: "取消", btn_confirm: "确认执行", btn_close: "关闭", btn_run: "执行",
    log_title: "后台任务",
    footer_text: "本工具在本地运行，不收集任何数据。修复前建议先阅读每项说明。",
    confirm_title: "确认执行：", risk_level: "风险等级：", admin_required: "（需要管理员权限）",
    parsing: "解析中…", parse_fail: "解析失败", req_fail: "请求失败：",
    scanning: "体检中…（读取显卡/注册表/进程）",
    plate_no_conflict: "未检测到已知冲突软件",
    hags_on: "HAGS 开启（与 DXGI 崩溃相关，建议关闭）",
    hags_off: "HAGS 已关闭",
    hags_unknown: "HAGS：%s",
    dual_gpu: "双显卡机型（注意 GPU 分配）", single_gpu: "单显卡",
    we_installed: "已安装", we_missing: "未定位到安装目录",
    dep_missing: "缺失 32 位依赖：%s", dep_ok: "32 位依赖完整",
    evt_unavail: "事件日志读取不可用",
    evt_err: "近 50 条显示/驱动错误：%s", evt_ok: "近期无显示驱动错误",
    label_os: "系统", label_gpu: "显卡",
    running_proc: "运行进程：", install_path: "安装目录：", read_fail: "部分子项读取失败：",
    env_detected: "识别到的环境：",
    summary_prefix: "结论：", suggestion: "建议：",
    admin_yes: "✓ 管理员权限", admin_no: "⚠ 非管理员（部分修复不可用）",
    yes: "是", no: "否", unknown_state: "未知",
    alert_no_text: "请先上传文件或粘贴诊断文本。",
    alert_sample_fail: "示例加载失败：",
    alert_exec_fail: "执行失败：",
    alert_admin: "需要管理员权限，请以管理员身份重新运行本程序。",
    alert_busy: "该任务正在进行中，请稍候。",
    guided_prefix: "（以上为引导步骤，本工具未自动修改系统）",
    alert_unfinished: "执行未完成：",
    log_waiting: "等待输出…", log_read_fail: "读取日志失败：",
    log_timeout: "[超时] 任务未能在预期时间内完成，可稍后手动重新体检。",
    lang_toggle_aria: "切换界面语言（中文/English）",
    theme_toggle_aria_light: "切换到夜间模式",
    theme_toggle_aria_dark: "切换到日间模式",
    sev_critical: "严重", sev_warning: "警告", sev_info: "提示", sev_ok: "正常",
    tag_risk: "风险", tag_admin: "需管理员", tag_type: "类型",
  },
  en: {
    app_title: "Wallpaper Fixer",
    brand_name: "Wallpaper Fixer",
    brand_sub: "Local scan · Health check · One-click fix",
    brand_aria: "Wallpaper Fixer home",
    nav_diag: "Diagnostic", nav_scan: "Health Check", nav_fix: "Fixes",
    nav_open: "Open navigation menu", nav_close: "Close navigation menu",
    btn_scan: "Health Check",
    hero_title: "Bring your wallpapers back to life",
    hero_sub: "A local Wallpaper Engine troubleshooter. Upload a diagnostic file, inspect your machine's graphics state, and apply fixes on demand — fully offline, no data leaves your PC.",
    hero_pill1: "① Analyze diagnostic file", hero_pill2: "② Live health check", hero_pill3: "③ One-click fixes",
    hero_note: "Tip: to fix drivers or system files, right-click this app and choose <b>Run as administrator</b>.",
    card1_title: "① Diagnostic File Analysis", tag_diag: "Diagnostic",
    hint_diag: "Upload the info.txt exported by Wallpaper Engine, or paste the diagnostic text below. DXGI crashes, missing dependencies, and tray errors are detected automatically.",
    file_choose: "Choose info.txt",
    file_aria: "Choose diagnostic file info.txt (.txt/.log/.md)",
    filebox_aria: "Choose diagnostic file info.txt",
    btn_parse: "Parse diagnostic", btn_sample: "Load sample",
    ph_diag: "Or paste diagnostic text here…",
    card2_title: "② Live Health Check", tag_scan: "Check",
    hint_scan: "Read your real machine state: GPU & drivers, dual-GPU, HAGS state, running processes, conflicting software, and display errors in the event log.",
    scan_placeholder: "Click “Health Check” at the top-right or the button below to start.",
    btn_scan2: "Start health check",
    card3_title: "③ One-Click Fixes", tag_fix: "Fixes",
    hint_fix: "Every action asks for confirmation; actions touching drivers/system files need admin rights. Long tasks run in the background with live logs.",
    loading: "Loading…",
    btn_cancel: "Cancel", btn_confirm: "Confirm", btn_close: "Close", btn_run: "Run",
    log_title: "Background task",
    footer_text: "This tool runs locally and collects no data. Please read each item's description before fixing.",
    confirm_title: "Confirm: ", risk_level: "Risk level: ", admin_required: " (admin required)",
    parsing: "Parsing…", parse_fail: "Parse failed", req_fail: "Request failed: ",
    scanning: "Scanning… (reading GPU/registry/processes)",
    plate_no_conflict: "No known conflicting software",
    hags_on: "HAGS enabled (linked to DXGI crashes — recommend off)",
    hags_off: "HAGS disabled",
    hags_unknown: "HAGS: %s",
    dual_gpu: "Dual-GPU laptop (watch GPU assignment)", single_gpu: "Single GPU",
    we_installed: "Installed", we_missing: "Install path not found",
    dep_missing: "Missing 32-bit deps: %s", dep_ok: "32-bit deps complete",
    evt_unavail: "Event log unavailable",
    evt_err: "Recent display/driver errors (50): %s", evt_ok: "No recent display driver errors",
    label_os: "OS", label_gpu: "GPU",
    running_proc: "Running processes: ", install_path: "Install path: ", read_fail: "Some sub-items failed to read: ",
    env_detected: "Detected environment: ",
    summary_prefix: "Summary: ", suggestion: "Suggestion: ",
    admin_yes: "✓ Administrator", admin_no: "⚠ Not admin (some fixes unavailable)",
    yes: "Yes", no: "No", unknown_state: "unknown",
    alert_no_text: "Please upload a file or paste diagnostic text first.",
    alert_sample_fail: "Failed to load sample: ",
    alert_exec_fail: "Execution failed: ",
    alert_admin: "Admin rights required. Please re-run this app as administrator.",
    alert_busy: "That task is already running. Please wait.",
    guided_prefix: "(The above are guidance steps; this tool did not modify your system)",
    alert_unfinished: "Execution incomplete: ",
    log_waiting: "Waiting for output…", log_read_fail: "Failed to read log: ",
    log_timeout: "[Timeout] task did not finish in time; re-run a health check later.",
    lang_toggle_aria: "Switch interface language (中文/English)",
    theme_toggle_aria_light: "Switch to dark mode",
    theme_toggle_aria_dark: "Switch to light mode",
    sev_critical: "Critical", sev_warning: "Warning", sev_info: "Info", sev_ok: "OK",
    tag_risk: "Risk", tag_admin: "Admin", tag_type: "Type",
  },
};

// 后端修复项按 id 的英译（zh 回退到服务器原文）
const FIX_I18N = {
  set_dgpu: { en: { title: "Force Wallpaper Engine to high-performance GPU", description: "Write GpuPreference=2 (high performance) for wallpaper64.exe under DirectX UserGpuPreferences, so dual-GPU laptops don't assign the wallpaper engine to the integrated GPU and trigger DXGI device loss." } },
  disable_hags: { en: { title: "Disable Hardware-accelerated GPU Scheduling (HAGS)", description: "Set GraphicsDrivers\\HwSchMode to 2 (disabled). This setting is strongly linked to DXGI crashes on NVIDIA Blackwell + Win11 25H2; disabling often greatly reduces device loss. Requires restart. Admin required." } },
  run_sfc: { en: { title: "Run sfc /scannow to repair system files", description: "Scan and repair possibly corrupted system files (including DirectX/DXGI related). Takes a few minutes, runs in the background. Admin required." } },
  run_dism: { en: { title: "Run DISM to repair system image", description: "Repair the Windows component store online (/RestoreHealth). Takes a while, runs in the background. Admin required." } },
  verify_steam_files: { en: { title: "Verify Wallpaper Engine game file integrity", description: "Open Steam and jump to the Wallpaper Engine page (appid 431960). Manually click Properties → Installed Files → Verify integrity of game files to restore missing 32-bit CEF/Assimp dependencies." } },
  detect_conflicts: { en: { title: "Check third-party shell interference (Windhawk / Winstep)", description: "List third-party programs that may interfere with the shell tray/graphics stack, and suggest temporarily exiting them or a clean boot. This action does not end any process automatically." } },
  reinstall_driver: { en: { title: "Guide: clean GPU driver reinstall", description: "Open NVIDIA's official driver page and the DDU guide. Recommended: use DDU in safe mode to fully uninstall NVIDIA+Intel drivers, then clean-install." } },
  open_graphics_settings: { en: { title: "Open Windows Graphics Settings (set GPU manually)", description: "Open Settings → System → Display → Graphics, where you can manually assign “High performance” to wallpaper64.exe." } },
};

// 后端诊断 findings 按 id 的英译（detail 用占位符动态拼接）
const FIND_I18N = {
  dxgi_device_lost: {
    en: {
      title: "Repeated GPU render crash (DXGI device lost)",
      rec: "Priority: ① clean-reinstall NVIDIA/Intel drivers with DDU in safe mode; ② force the wallpaper engine to the discrete GPU; ③ disable HAGS; ④ check GPU switching on dual-GPU laptops.",
      detail: (f) => `The log shows ${f.count} “DXGI device lost” event(s). The classic “lost → recover → lost again” loop points to a broken contract between the GPU driver and the system graphics stack.`,
    },
  },
  deps_missing_x86: {
    en: {
      title: "Missing 32-bit dependencies (CEF / Assimp loaded:0)",
      rec: "Most often caused by a broken install (failed update / blocked by antivirus). Go to Steam → Library → Wallpaper Engine → Properties → Installed Files → Verify integrity of game files; this usually restores the missing DLLs.",
      detail: (f) => {
        const list = (f.evidence || []).map((e) => e.split("->").pop().trim()).filter(Boolean);
        const cef = list.some((d) => /cef|chrome_elf|libegl|libglesv2/i.test(d));
        const assimp = list.some((d) => /assimp/i.test(d));
        let s = `Detected ${list.length} 32-bit dependenc(ies) that failed to load: ${list.join(", ")}.`;
        if (cef) s += " Missing CEF/Chromium components break Web/HTML wallpapers;";
        if (assimp) s += " Missing Assimp affects 3D/Scene wallpaper import.";
        return s;
      },
    },
  },
  tray_icon_fail: {
    en: {
      title: "System tray icon creation failed (E_FAIL)",
      rec: "Check third-party shell programs: temporarily exit Winstep Xtreme / Windhawk, or use msconfig for a clean boot and see if it disappears.",
      detail: (f) => `Tray icon creation failed ${f.count} time(s) (E_FAIL), usually caused by third-party shell enhancements (Winstep / Windhawk injecting into explorer). Does not affect wallpaper rendering, but may cause occasional tray icon/context-menu glitches.`,
    },
  },
  web_script_error: {
    en: {
      title: "Web/HTML wallpaper script error",
      rec: "If a specific wallpaper triggers it, switch to another one; if many Web wallpapers error out, fix the CEF dependency above first.",
      detail: (f) => `Detected ${f.count} Web/HTML wallpaper script error(s). Most are bugs in individual wallpapers (running before the engine injects the scene API), not the engine itself; a few may stem from CEF component issues.`,
    },
  },
  cef_ui_glitch: {
    en: {
      title: "UI-layer CEF occasional glitch",
      rec: "Usually harmless; if it happens often, fix it together with the CEF dependency above.",
      detail: () => "The engine UI occasionally fails to load local resources/callbacks. Lowest-priority UI glitch.",
    },
  },
  no_issue: {
    en: {
      title: "No known failure patterns detected",
      rec: "If problems persist, make sure the exported diagnostic is complete or describe the specific symptom.",
      detail: () => "No typical signals (DXGI crash, missing deps, tray error, script error) were found in the current text.",
    },
  },
};

let curLang = "zh";
let curTheme = "light";

function t(key) {
  const d = I18N[curLang] || I18N.zh;
  return (key in d) ? d[key] : (I18N.zh[key] != null ? I18N.zh[key] : key);
}
function tf(key, ...args) {
  let s = t(key);
  args.forEach((a) => { s = s.replace("%s", a); });
  return s;
}
function sevLabel(s) {
  return t("sev_" + (s || "")) || s;
}
function fixDisplay(a) {
  const o = (FIX_I18N[a.id] && FIX_I18N[a.id][curLang]) || {};
  return { title: o.title || a.title, description: o.description || a.description };
}
function findingDisplay(f) {
  const o = (FIND_I18N[f.id] && FIND_I18N[f.id][curLang]) || {};
  return {
    title: o.title || f.title,
    detail: (o.detail ? o.detail(f) : f.detail) || "",
    recommendation: o.rec || f.recommendation || "",
  };
}

// 静态文本 i18n：textContent + 属性
// 注：data-i18n-html 仅用于本工具自带的、可信的常量（含 <b> 等强调标签），
// 绝不用于任何用户输入，因此无 XSS 风险。
function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.getAttribute("data-i18n-html"));
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
    el.getAttribute("data-i18n-attr").split(";").forEach((pair) => {
      const idx = pair.indexOf(":");
      if (idx < 0) return;
      const attr = pair.slice(0, idx).trim();
      const key = pair.slice(idx + 1).trim();
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
  document.title = t("app_title");
}

function updateLangToggle() {
  const b = $("langToggle");
  if (!b) return;
  b.textContent = curLang === "zh" ? "EN" : "中文";
  b.setAttribute("aria-label", t("lang_toggle_aria"));
}

function setLang(lang) {
  curLang = lang === "en" ? "en" : "zh";
  document.documentElement.lang = curLang === "en" ? "en" : "zh-CN";
  try { localStorage.setItem("wf_lang", curLang); } catch (e) {}
  updateLangToggle();
  applyStaticI18n();
  // 重渲染动态内容
  if (lastFixes) renderFixes(lastFixes);
  if (lastParse) renderParse(lastParse);
  if (lastSystem) renderSystem(lastSystem);
  if (lastIsAdmin !== null) updateAdmin(lastIsAdmin);
  if (pendingAction && !$("modal").classList.contains("hidden")) openConfirm(pendingAction);
  if (!$("logModal").classList.contains("hidden") && currentLogTask) {
    $("logTitle").textContent = t("log_title") + currentLogTask;
  }
}

function setTheme(theme) {
  curTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.classList.toggle("theme-dark", curTheme === "dark");
  try { localStorage.setItem("wf_theme", curTheme); } catch (e) {}
  const tt = $("themeToggle");
  if (tt) tt.setAttribute("aria-label", curTheme === "dark" ? t("theme_toggle_aria_dark") : t("theme_toggle_aria_light"));
}

/* ============================================================
   通用工具
   ============================================================ */
async function api(url, opts = {}, timeoutMs = 30000) {
  const ctrl = new AbortController();
  const tid = setTimeout(() => ctrl.abort(), timeoutMs);
  let data = {};
  try {
    const r = await fetch(url, { ...opts, signal: ctrl.signal });
    try { data = await r.json(); } catch (e) { data = {}; }
    if (!r.ok) data = { ...data, _http: r.status, ok: false };
  } catch (e) {
    clearTimeout(tid);
    if (e && e.name === "AbortError") throw new Error(t("req_fail") + "timeout");
    throw e;
  }
  clearTimeout(tid);
  return data;
}

function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html !== undefined) e.innerHTML = html;
  return e;
}

// 用 textContent 构建节点：诊断文件/系统信息里可能含 < & 等字符，
// 直接用 innerHTML 会被当 HTML 解析，既会渲染错乱也是 XSS 隐患。
function elText(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  e.textContent = (text == null) ? "" : String(text);
  return e;
}

// 转义用于 innerHTML 插值的动态文本
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// 修复项底部的小标签（风险 / 管理员 / 类型），保持对齐且语义配色
function tagEl(label, value, emphasis) {
  const s = el("span", "risk-tag" + (emphasis ? " need-admin" : ""));
  s.innerHTML = `${esc(label)} <b>${esc(value)}</b>`;
  return s;
}

/* ============================================================
   诊断文件解析
   ============================================================ */
let lastParse = null;

async function doParse(text) {
  const box = $("parseResult");
  box.innerHTML = `<div class="placeholder">${esc(t("parsing"))}</div>`;
  try {
    const res = await api("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) { box.innerHTML = `<div class="placeholder">${esc(res.error || t("parse_fail"))}</div>`; return; }
    renderParse(res);
  } catch (e) {
    box.innerHTML = `<div class="placeholder">${esc(t("req_fail") + String(e))}</div>`;
  }
}

function renderParse(res) {
  lastParse = res;
  const box = $("parseResult");
  box.innerHTML = "";
  box.appendChild(elText("div", "summary", t("summary_prefix") + (res.summary || "")));

  if (res.meta && Object.keys(res.meta).length) {
    const metaStr = t("env_detected") + Object.entries(res.meta)
      .map(([k, v]) => `${k}=${Array.isArray(v) ? v.join(", ") : v}`).join(" · ");
    const m = elText("div", "muted", metaStr);
    m.style.fontSize = "12px"; m.style.margin = "6px 0";
    box.appendChild(m);
  }

  const list = el("div", "findings");
  res.findings.forEach((f) => {
    const d = findingDisplay(f);
    const card = el("div", `finding ${f.severity}`);
    const h = document.createElement("h3");
    h.appendChild(elText("span", null, d.title || ""));
    if (f.count != null) {
      const c = elText("span", "muted", ` (×${f.count})`);
      h.appendChild(c);
    }
    h.appendChild(el("span", `sev ${f.severity}`, sevLabel(f.severity)));
    card.appendChild(h);
    if (d.detail) card.appendChild(elText("div", "detail", d.detail));
    if (d.recommendation) card.appendChild(elText("div", "rec", t("suggestion") + d.recommendation));
    if (f.evidence && f.evidence.length) {
      card.appendChild(elText("pre", "ev", f.evidence.map((x) => "• " + x).join("\n")));
    }
    list.appendChild(card);
  });
  box.appendChild(list);
}

$("parseBtn").onclick = () => {
  const txt = $("diagText").value.trim();
  if (!txt) { alert(t("alert_no_text")); return; }
  doParse(txt);
};
$("fileInput").onchange = (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const reader = new FileReader();
  reader.onload = () => { $("diagText").value = reader.result; doParse(reader.result); };
  reader.readAsText(f);
};
// 可访问性：label 可键盘聚焦，回车/空格触发文件选择
$("fileInput").closest("label").addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("fileInput").click(); }
});
$("loadSampleBtn").onclick = async () => {
  try {
    const txt = await (await fetch("/sample_info.txt")).text();
    $("diagText").value = txt;
    doParse(txt);
  } catch (e) { alert(t("alert_sample_fail") + e); }
};

/* ============================================================
   系统体检
   ============================================================ */
let scanning = false;
let lastSystem = null;

function doScan() {
  if (scanning) return;
  scanning = true;
  const box = $("systemResult");
  box.innerHTML = `<div class="placeholder">${esc(t("scanning"))}</div>`;
  api("/api/system", {}, 60000)
    .then((res) => {
      if (res.busy) { box.innerHTML = `<div class="placeholder">${esc(res.message || "")}</div>`; return; }
      if (res.platform_unsupported) { box.innerHTML = `<div class="placeholder">${esc(res.message || "")}</div>`; return; }
      renderSystem(res, box);
    })
    .catch((e) => { box.innerHTML = `<div class="placeholder">${esc(t("req_fail") + String(e))}</div>`; })
    .finally(() => { scanning = false; });
}
$("scanBtn").onclick = doScan;
$("scanBtn2").onclick = doScan;

function renderSystem(res, box) {
  lastSystem = res;
  box.innerHTML = "";
  const os = res.os || {};
  const gpus = res.gpus || [];

  const conflicts = res.conflicts || [];
  const conflictHtml = conflicts.length
    ? conflicts.map((c) => `<span class="pill bad">${esc(c)}</span>`).join("")
    : `<span class="pill good">${esc(t("plate_no_conflict"))}</span>`;

  const hags = res.hags || {};
  const hagsHtml = hags.enabled === true
    ? `<span class="pill bad">${esc(t("hags_on"))}</span>`
    : hags.enabled === false
      ? `<span class="pill good">${esc(t("hags_off"))}</span>`
      : `<span class="pill warn">${esc(tf("hags_unknown", hags.note || t("unknown_state")))}</span>`;

  const dualHtml = res.dual_gpu
    ? `<span class="pill warn">${esc(t("dual_gpu"))}</span>`
    : `<span class="pill good">${esc(t("single_gpu"))}</span>`;

  const we = res.wallpaper_engine || {};
  const weHtml = we.installed
    ? `<span class="pill good">${esc(t("we_installed"))}</span>`
    : `<span class="pill warn">${esc(t("we_missing"))}</span>`;
  const miss = we.missing_x86_dlls || [];
  const missHtml = miss.length
    ? `<span class="pill bad">${esc(tf("dep_missing", miss.join(", ")))}</span>`
    : `<span class="pill good">${esc(t("dep_ok"))}</span>`;

  const dxgi = res.dxgi_event_errors;
  const dxgiHtml = dxgi == null
    ? `<span class="pill warn">${esc(t("evt_unavail"))}</span>`
    : dxgi > 0
      ? `<span class="pill bad">${esc(tf("evt_err", String(dxgi)))}</span>`
      : `<span class="pill good">${esc(t("evt_ok"))}</span>`;

  const gpuLine = gpus.map((g) => esc(`${g.Name} (driver ${g.DriverVersion}, ${g.Status})`)).join("<br>");
  const head = el("div", null,
    `<div class="kv">
      <div class="k">${esc(t("label_os"))}</div><div class="v">${esc(os.Caption || "?")} · Build ${esc(os.BuildNumber || "?")}</div>
      <div class="k">${esc(t("label_gpu"))}</div><div class="v">${gpuLine}</div>
    </div>
    <div>${dualHtml} ${hagsHtml} ${weHtml} ${missHtml} ${dxgiHtml}</div>
    <div style="margin-top:8px">${conflictHtml}</div>`);
  box.appendChild(head);

  const procs = res.processes || {};
  const procLines = Object.entries(procs).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(",") : v}`).join(" · ");
  if (procLines) {
    const pm = elText("div", "muted", t("running_proc") + procLines);
    pm.style.fontSize = "12px"; pm.style.marginTop = "10px";
    box.appendChild(pm);
  }
  if (we.path) box.appendChild(elText("div", "muted", t("install_path") + we.path));
  if (res.errors && res.errors.length) {
    const er = elText("div", "muted", t("read_fail") + res.errors.join("; "));
    er.style.fontSize = "12px"; er.style.color = "var(--warning)";
    box.appendChild(er);
  }
}

/* ============================================================
   修复列表
   ============================================================ */
let pendingAction = null;
let lastFixes = null;

function loadFixes() {
  api("/api/fixes")
    .then((res) => {
      updateAdmin(res.is_admin);
      renderFixes(res);
    })
    .catch((e) => { $("fixList").innerHTML = `<div class="placeholder">${esc(t("req_fail") + String(e))}</div>`; });
}

function renderFixes(res) {
  lastFixes = res;
  const box = $("fixList");
  box.innerHTML = "";
  (res.actions || []).forEach((a) => {
    const disp = fixDisplay(a);
    const card = el("div", "fix");
    const top = el("div", "fix-top");
    const title = el("h3", "fix-title", disp.title);
    const act = el("div", "fix-act");
    const btn = el("button", "btn btn-primary", t("btn_run"));
    btn.onclick = () => openConfirm(a);
    act.appendChild(btn);
    top.appendChild(title); top.appendChild(act);

    const desc = el("p", "fix-desc", disp.description);

    const risk = el("div", "fix-risk");
    risk.appendChild(tagEl(t("tag_risk"), a.risk, false));
    risk.appendChild(tagEl(t("tag_admin"), a.needs_admin ? t("yes") : t("no"), a.needs_admin));
    risk.appendChild(tagEl(t("tag_type"), a.kind, false));

    card.appendChild(top);
    card.appendChild(desc);
    card.appendChild(risk);
    box.appendChild(card);
  });
}

let lastIsAdmin = null;
function updateAdmin(isAdmin) {
  lastIsAdmin = isAdmin;
  const b = $("adminBadge");
  if (isAdmin) { b.textContent = t("admin_yes"); b.className = "badge badge-ok"; }
  else { b.textContent = t("admin_no"); b.className = "badge badge-warn"; }
}

function openConfirm(a) {
  pendingAction = a;
  const disp = fixDisplay(a);
  $("modalTitle").textContent = t("confirm_title") + disp.title;
  $("modalDesc").textContent = disp.description;
  $("modalRisk").textContent = t("risk_level") + a.risk + (a.needs_admin ? t("admin_required") : "");
  $("modal").classList.remove("hidden");
  $("modalOk").focus();
}
$("modalCancel").onclick = () => { $("modal").classList.add("hidden"); pendingAction = null; };
$("modalOk").onclick = () => {
  const a = pendingAction;
  $("modal").classList.add("hidden");
  pendingAction = null;
  if (!a) return;
  api("/api/fix/" + a.id, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirm: true }),
  })
    .then((res) => handleFixResult(a, res))
    .catch((e) => alert(t("alert_exec_fail") + e));
};

function handleFixResult(a, res) {
  if (res.need_confirm) { openConfirm(a); return; }
  if (res.needs_admin) { alert(res.message || t("alert_admin")); return; }
  if (res.busy) { alert(res.message || t("alert_busy")); return; }
  if (res.guided) {
    alert(a.title + "\n\n" + (res.message || a.description) + "\n\n" + t("guided_prefix"));
    return;
  }
  if (res.async) { startLog(a.title, a.id); return; }
  if (res.ok) { alert(a.title + "\n" + (res.stdout || "")); doScan(); }
  else { alert(t("alert_unfinished") + (res.error || res.stderr || "unknown")); }
}

/* ============================================================
   后台日志
   ============================================================ */
let logTimer = null;
let currentLogTask = "";

function startLog(title, actionId) {
  currentLogTask = title;
  $("logTitle").textContent = t("log_title") + title;
  $("logBody").textContent = t("log_waiting");
  $("logModal").classList.remove("hidden");
  if (logTimer) clearInterval(logTimer);
  let tries = 0;
  const MAX_TRIES = 90;
  logTimer = setInterval(async () => {
    try {
      const r = await api("/api/fix/log?action=" + encodeURIComponent(actionId));
      if (r.error) {
        clearInterval(logTimer); logTimer = null;
        $("logBody").textContent = t("log_read_fail") + r.error;
        return;
      }
      if (r.exists) {
        $("logBody").textContent = r.lines.join("\n");
        $("logBody").scrollTop = $("logBody").scrollHeight;
        if (r.done) { clearInterval(logTimer); logTimer = null; doScan(); return; }
      }
      if (++tries > MAX_TRIES) {
        clearInterval(logTimer); logTimer = null;
        $("logBody").textContent += "\n" + t("log_timeout");
      }
    } catch (e) { /* 忽略单次轮询错误 */ }
  }, 2000);
}

$("logClose").onclick = () => {
  if (logTimer) { clearInterval(logTimer); logTimer = null; }
  $("logModal").classList.add("hidden");
};

/* ============================================================
   导航：移动端汉堡菜单
   ============================================================ */
(function initNav() {
  const toggle = $("navToggle");
  const menu = $("navMenu");
  if (!toggle || !menu) return;
  toggle.setAttribute("aria-label", t("nav_open"));
  toggle.addEventListener("click", () => {
    const openState = menu.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(openState));
    toggle.setAttribute("aria-label", openState ? t("nav_close") : t("nav_open"));
  });
  menu.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", () => {
      if (window.matchMedia("(max-width: 760px)").matches) {
        menu.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", t("nav_open"));
      }
    });
  });
  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 761px)").matches && menu.classList.contains("open")) {
      menu.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", t("nav_open"));
    }
  });
})();

/* ============================================================
   滚动淡入动画
   ============================================================ */
(function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window) || !items.length) {
    items.forEach((el) => el.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
  items.forEach((el) => io.observe(el));
})();

/* ============================================================
   无障碍：Esc 关闭任意打开的模态框
   ============================================================ */
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (!$("logModal").classList.contains("hidden")) { $("logClose").click(); }
  else if (!$("modal").classList.contains("hidden")) { $("modalCancel").click(); }
});

(async function boot() {
  // 还原语言偏好（主题已由 head 内联脚本在 CSS 前应用，避免闪白）
  try {
    const saved = localStorage.getItem("wf_lang");
    if (saved === "en" || saved === "zh") curLang = saved;
  } catch (e) {}
  curTheme = document.documentElement.classList.contains("theme-dark") ? "dark" : "light";

  updateLangToggle();
  setTheme(curTheme);       // 仅用于设置 aria-label（class 已就绪）
  applyStaticI18n();

  $("langToggle").onclick = () => setLang(curLang === "zh" ? "en" : "zh");
  $("themeToggle").onclick = () => setTheme(curTheme === "dark" ? "light" : "dark");

  try { updateAdmin((await api("/api/health")).admin); } catch (e) {}
  loadFixes();
})();
