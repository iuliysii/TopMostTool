#!/bin/bash
# macOS 打包脚本
# 使用 py2app 创建 macOS 应用程序包

# 检查是否在 macOS 上运行
if [[ "$(uname)" != "Darwin" ]]; then
    echo "错误: 此脚本只能在 macOS 上运行"
    exit 1
fi

# 设置变量
APP_NAME="TopMost Tool"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist"
BUILD_DIR="${SCRIPT_DIR}/build"

echo "=========================================="
echo "  TopMost Tool - macOS 打包脚本"
echo "=========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

# 安装依赖
echo ""
echo "[1/4] 安装依赖..."
pip3 install -r requirements.txt

# 安装打包工具
echo ""
echo "[2/4] 安装打包工具..."
pip3 install py2app

# 清理旧构建
echo ""
echo "[3/4] 清理旧构建..."
rm -rf "${BUILD_DIR}"
rm -rf "${DIST_DIR}"

# 创建 setup.py 用于 py2app
cat > "${SCRIPT_DIR}/setup_py2app.py" << 'SETUP_EOF'
from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('locales', ['locales/zh_CN.json', 'locales/en.json']),
    ('assets', ['assets/icon.png']),
]

OPTIONS = {
    'argv_emulation': False,
    'packages': ['objc', 'Quartz', 'AppKit', 'Cocoa', 'pynput', 'PIL', 'pystray'],
    'includes': [
        'objc',
        'Quartz',
        'Quartz.CoreGraphics',
        'Quartz.QuartzCore',
        'AppKit',
        'Cocoa',
        'pynput',
        'pynput.keyboard',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'pystray',
        'pystray._darwin',
    ],
    'excludes': ['tkinter', 'matplotlib', 'numpy'],
    'iconfile': 'assets/icon.icns',
    'plist': {
        'CFBundleName': 'TopMost Tool',
        'CFBundleDisplayName': 'TopMost Tool',
        'CFBundleIdentifier': 'com.topmost.tool',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # 隐藏 Dock 图标，只显示在菜单栏
        'NSAppleEventsUsageDescription': 'This app needs to control other applications to manage window states.',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
SETUP_EOF

# 构建
echo ""
echo "[4/4] 构建应用程序..."
cd "${SCRIPT_DIR}"
python3 setup_py2app.py py2app

# 清理临时文件
rm -f "${SCRIPT_DIR}/setup_py2app.py"

# 检查结果
if [[ -d "${DIST_DIR}/${APP_NAME}.app" ]]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 打包成功!"
    echo "=========================================="
    echo ""
    echo "应用程序位置: ${DIST_DIR}/${APP_NAME}.app"
    echo ""
    echo "使用方法:"
    echo "  1. 双击 ${APP_NAME}.app 运行"
    echo "  2. 或拖拽到 Applications 文件夹安装"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 打包失败"
    echo "=========================================="
    exit 1
fi
