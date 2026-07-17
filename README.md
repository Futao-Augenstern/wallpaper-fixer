<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-blue?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs" />
</p>

<h1 align="center">🛠 Wallpaper 修复助手</h1>
<p align="center"><strong>本地诊断 · 系统体检 · 一键修复</strong></p>
<p align="center">专治 Wallpaper Engine 各种疑难杂症：DXGI 崩溃、依赖缺失、托盘报错……</p>

---

## 它能做什么

Wallpaper Engine 的常见故障本质上是 Windows 系统级问题——显卡驱动、双显卡切换、HAGS、系统文件损坏、第三方软件冲突。这些浏览器沙箱无法触碰，所以本工具做成**本地桌面应用**：Python 后端执行系统命令做真修复，配合本地 Web 界面交互。

- **上传诊断文件** → 自动识别 `DXGI device lost`、`0x8876017C`、32 位 CEF/Assimp 缺失、托盘 `E_FAIL`、Web 壁纸脚本报错
- **实时系统体检** → 读取显卡型号/驱动版本、双显卡、HAGS 开关、运行进程、冲突软件、事件日志错误
- **一键修复（二次确认）** → 强制独显、关闭 HAGS、sfc / DISM 修复、验证 Steam 文件、引导清洁重装驱动

> 🔒 **全程不联网、不上传任何数据。**

---

## 快速开始

### 方式一：双击运行（推荐）

```
双击 run.bat 即可启动
```

首次运行会自动创建虚拟环境并安装依赖，之后直接启动。浏览器自动打开 `http://127.0.0.1:8520`。

> 需要修复驱动或系统文件时，请**右键 run.bat → 以管理员身份运行**。

### 方式二：命令行

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动
python app.py
```

端口可通过环境变量自定义：`WF_PORT=9000 python app.py`

---

## 截图

| 诊断分析 | 系统体检 |
|:---:|:---:|
| 上传 info.txt 或粘贴诊断文本，自动定位问题 | 读取显卡、HAGS、进程、事件日志等真实状态 |

| 一键修复 | 后台日志 |
|:---:|:---:|
| 每项操作二次确认，风险等级明确 | 耗时操作后台执行，实时查看进度 |

---

## 目录结构

```
wallpaper-fixer/
├── app.py                 # Flask 后端（界面 + API）
├── run.bat                # 一键启动脚本
├── requirements.txt
├── lib/
│   ├── parser.py          # 诊断文件解析（纯 Python，可单测）
│   ├── system_info.py     # 实时系统体检（PowerShell/WMI）
│   └── fixes.py           # 修复动作定义与执行
├── static/
│   ├── index.html         # Web 界面（支持中/英、暗色主题）
│   ├── app.js
│   ├── style.css
│   └── sample_info.txt    # 示例诊断数据
└── tests/
    ├── test_parser.py     # 解析器测试
    ├── test_fixes.py      # 修复逻辑测试
    ├── test_security.py   # 安全测试（注入防护、路径穿越）
    └── test_system.py     # 体检解析测试
```

---

## 修复动作一览

| 动作 | 类型 | 需要管理员 | 风险 |
|------|------|:---:|:---:|
| 强制壁纸引擎走独显 | 注册表修改 | | 低 |
| 关闭 HAGS | 注册表修改 | ✓ | 低 |
| sfc /scannow | 系统命令 | ✓ | 低 |
| DISM 修复 | 系统命令 | ✓ | 低 |
| 验证 Steam 文件完整性 | 引导 | | 无 |
| 排查第三方冲突 | 引导 | | 无 |
| 引导驱动清洁重装 | 引导 | | 无 |
| 打开图形设置 | 引导 | | 无 |

---

## 安全说明

- 所有改动系统的操作都需要用户**二次确认**
- 需要管理员权限的操作在未提权时会明确提示
- `guided` 类操作不改动系统，仅打开设置页/网页并给出指引
- 本工具**不收集、不上传任何数据**，全部在本地运行

---

## 已知限制

- 仅支持 Windows 10/11（系统体检依赖 PowerShell/WMI）
- 显卡偏好写入注册表后，部分机型仍需在 Windows 图形设置中手动确认
- HAGS 关闭后需**重启系统**才能完全生效

---

## 开发

```bash
# 运行测试
python -m pytest tests/ -v

# 或使用 unittest
python -m unittest discover tests -v
```

---

## 许可证

[MIT](LICENSE) © Futao-Augenstern