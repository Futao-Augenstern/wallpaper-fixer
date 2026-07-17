"""
Wallpaper Engine 修复工具 —— 本地桌面应用后端
------------------------------------------------
Flask 提供本地 Web 界面 + API。启动方式：
    python app.py
然后浏览器打开 http://127.0.0.1:8520

所有“改动系统”的修复都要求前端二次确认，且需要管理员权限的动作会在未提权时明确提示。
"""

from __future__ import annotations

import os
import sys

from flask import Flask, request, jsonify, send_from_directory

# 让 lib 可被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import parser, system_info, fixes  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 运行端口与输入边界
DEFAULT_PORT = 8520
MAX_CONTENT_LENGTH = 2 * 1024 * 1024   # 上传文件 / 请求体上限 2MB
MAX_TEXT_CHARS = 1_000_000            # 粘贴文本上限（约 1MB，防止超大负载）

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


@app.errorhandler(413)
def _too_large(_e):
    return jsonify({"ok": False, "error": "诊断内容过大（上限 2MB）。请上传原始 info.txt，或精简后粘贴。"}), 413


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/parse", methods=["POST"])
def api_parse():
    text = ""
    source = "upload"
    if "file" in request.files:
        f = request.files["file"]
        source = f.filename or "upload"
        text = f.read().decode("utf-8", errors="ignore")
    elif request.is_json and request.json.get("text"):
        text = request.json["text"]
        source = "paste"
        if len(text) > MAX_TEXT_CHARS:
            return jsonify({"ok": False, "error": "粘贴文本过长（上限约 1MB）。请上传原始 info.txt。"}), 413
    if not text.strip():
        return jsonify({"ok": False, "error": "未收到诊断内容。请上传 info.txt 或粘贴文本。"})
    result = parser.parse_diagnostic(text, source=source)
    return jsonify({"ok": True, **result.to_dict()})


@app.route("/api/system", methods=["GET"])
def api_system():
    info = system_info.collect_system_info()
    if info.get("busy"):
        return jsonify({"ok": False, **info}), 429
    return jsonify({"ok": True, **info})


@app.route("/api/fixes", methods=["GET"])
def api_fixes():
    return jsonify({"ok": True, "actions": fixes.list_actions(),
                    "is_admin": fixes.is_admin()})


@app.route("/api/fix/<action_id>", methods=["POST"])
def api_fix(action_id: str):
    data = request.get_json(silent=True) or {}
    confirm = bool(data.get("confirm", False))
    params = data.get("params")
    result = fixes.run_fix(action_id, confirm=confirm, params=params)
    return jsonify(result)


@app.route("/api/fix/log", methods=["GET"])
def api_fix_log():
    action = request.args.get("action", "")
    if not fixes.is_known_action(action):
        return jsonify({"ok": False, "error": "无效的 action 参数"}), 400
    return jsonify({"ok": True, **fixes.get_fix_log(action)})


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"ok": True, "admin": fixes.is_admin()})


def main():
    import threading
    import webbrowser

    port = int(os.environ.get("WF_PORT", str(DEFAULT_PORT)))
    url = f"http://127.0.0.1:{port}"
    print(f"[Wallpaper Engine 修复工具] 正在启动： {url}")
    print("提示：需要修复驱动/系统文件时，请务必以管理员身份运行本程序。")
    # 启动后自动打开浏览器
    threading.Timer(1.5, lambda: (webbrowser.open(url) if not os.environ.get("WF_NO_BROWSER") else None)).start()
    # waitress 生产级本地服务；缺失时回退到 Flask 内置
    try:
        from waitress import serve
        serve(app, host="127.0.0.1", port=port)
    except Exception:
        app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
