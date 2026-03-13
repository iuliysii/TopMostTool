@echo off
REM Windows 打包脚本
REM 使用 PyInstaller 创建 Windows 可执行文件

echo ==========================================
echo   TopMost Tool - Windows 打包脚本
echo ==========================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    exit /b 1
)

REM 安装依赖
echo.
echo [1/4] 安装依赖...
pip install -r requirements.txt

REM 安装 PyInstaller
echo.
echo [2/4] 安装 PyInstaller...
pip install pyinstaller

REM 清理旧构建
echo.
echo [3/4] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 构建
echo.
echo [4/4] 构建可执行文件...
pyinstaller --noconsole --onefile --name "TopMostTool" --hidden-import pystray._win32 --icon "assets\icon.ico" --add-data "locales;locales" main.py

REM 检查结果
if exist "dist\TopMostTool.exe" (
    echo.
    echo ==========================================
    echo   打包成功!
    echo ==========================================
    echo.
    echo 可执行文件位置: dist\TopMostTool.exe
    echo.
    echo 使用方法:
    echo   右键 TopMostTool.exe -^> 以管理员身份运行
    echo.
) else (
    echo.
    echo ==========================================
    echo   打包失败
    echo ==========================================
    exit /b 1
)
