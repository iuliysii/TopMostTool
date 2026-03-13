#!/bin/bash
# Linux 打包脚本
# 使用 PyInstaller 创建 Linux 可执行文件

# 设置变量
APP_NAME="TopMostTool"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_DIR}/dist"
BUILD_DIR="${PROJECT_DIR}/build"

echo "=========================================="
echo "  TopMost Tool - Linux 打包脚本"
echo "=========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

# 检查是否在 Linux 上运行
if [[ "$(uname)" != "Linux" ]]; then
    echo "警告: 此脚本设计用于 Linux 系统"
fi

# 检查 X11
if ! command -v xdpyinfo &> /dev/null; then
    echo "警告: 未检测到 X11 环境"
    echo "请确保已安装 X11 开发库:"
    echo "  Ubuntu/Debian: sudo apt install libx11-dev libxext-dev"
    echo "  Fedora/RHEL:   sudo dnf install libX11-devel libXext-devel"
fi

# 安装依赖
echo ""
echo "[1/4] 安装依赖..."
pip3 install -r "${PROJECT_DIR}/requirements.txt"

# 安装 PyInstaller
echo ""
echo "[2/4] 安装 PyInstaller..."
pip3 install pyinstaller

# 清理旧构建
echo ""
echo "[3/4] 清理旧构建..."
rm -rf "${BUILD_DIR}"
rm -rf "${DIST_DIR}"

# 构建
echo ""
echo "[4/4] 构建可执行文件..."
cd "${PROJECT_DIR}"

pyinstaller \
    --noconsole \
    --onefile \
    --name "${APP_NAME}" \
    --hidden-import pystray._gtk \
    --hidden-import pynput.keyboard._xorg \
    --add-data "locales:locales" \
    main.py

# 检查结果
if [[ -f "${DIST_DIR}/${APP_NAME}" ]]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 打包成功!"
    echo "=========================================="
    echo ""
    echo "可执行文件位置: ${DIST_DIR}/${APP_NAME}"
    echo ""
    echo "使用方法:"
    echo "  chmod +x ${DIST_DIR}/${APP_NAME}"
    echo "  ./${DIST_DIR}/${APP_NAME}"
    echo ""
    echo "安装到系统 (可选):"
    echo "  sudo cp ${DIST_DIR}/${APP_NAME} /usr/local/bin/topmost-tool"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 打包失败"
    echo "=========================================="
    exit 1
fi
