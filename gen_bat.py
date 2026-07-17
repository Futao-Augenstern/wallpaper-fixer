# gen_bat.py - 生成 GBK 编码(无 BOM、CRLF)的 run.bat，规避 cmd 以 GBK 读 UTF-8 导致的乱码。
path = r"D:\workspace\a\wallpaper-fixer\run.bat"
batch = r'''@echo off
cd /d "%~dp0"

set "LOG=%TEMP%\wallpaper_fixer_run.log"
echo [%date% %time%] run.bat start > "%LOG%"

if /I "%~1"=="admin" (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY ( where python3 >nul 2>&1 && set "PY=python3" )
if not defined PY (
    echo [ERROR] 未检测到 Python。请安装 Python 3.10+ 并勾选 Add python.exe to PATH。
    echo 正在打开 Python 官网下载页...
    start "" "https://www.python.org/downloads/windows/"
    echo 详情见日志：%LOG%
    pause
    exit /b
)
echo [INFO] using: %PY% >> "%LOG%"

if not exist "venv\Scripts\python.exe" (
    echo 首次运行：创建虚拟环境并安装依赖（需要联网，约 1 分钟）...
    %PY% -m venv venv >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] 创建虚拟环境失败，详见 %LOG%
        pause
        exit /b
    )
    venv\Scripts\pip install -r requirements.txt >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] 安装依赖失败（可能无网络或被墙）。详见 %LOG%
        echo          可手动执行：venv\Scripts\pip install -r requirements.txt
        pause
        exit /b
    )
    echo 依赖安装完成。>> "%LOG%"
)

echo.
echo 启动 Wallpaper Engine 修复工具...
echo 浏览器将自动打开 http://127.0.0.1:8520
echo 如需修复驱动或系统文件，请右键本文件 - 以管理员身份运行
echo 运行日志：%LOG%
echo.
venv\Scripts\python app.py
echo.
echo [程序已退出] 按任意键关闭。若启动失败请查看 %LOG%
pause
'''
data = batch.replace("\n", "\r\n").encode("gbk")
with open(path, "wb") as f:
    f.write(data)
print("written bytes:", len(data))
print("starts with BOM:", data[:3] == b"\xef\xbb\xbf")
