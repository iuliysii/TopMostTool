"""
main.py  —  集成入口：串联四个模块，启动托盘主循环
用法：python main.py
注意：需要管理员权限运行（keyboard 全局钩子 + Win32 置顶操作）
"""

import logging
import sys

# ── 统一日志格式（必须在所有模块 import 之前配置）──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("main")

# ── 导入四个模块 ──────────────────────────────────
try:
    from config import config_manager
    from core import hotkey_listener
    from core import window_manager
    from ui.tray_app import TrayApp
except ImportError as e:
    log.error(f"模块导入失败: {e}")
    log.error("请确认已安装依赖：pip install -r requirements.txt")
    sys.exit(1)


# ════════════════════════════════════════════════
# 模块级全局状态
# ════════════════════════════════════════════════

# 本工具管理的置顶窗口句柄集合（只记录由本工具置顶的窗口）
_managed_hwnds: set[int] = set()

# 托盘实例（在 main() 中赋值，回调函数中使用）
_tray: TrayApp | None = None


# ════════════════════════════════════════════════
# 快捷键回调
# ════════════════════════════════════════════════

def on_hotkey_triggered() -> None:
    """
    快捷键触发时的处理逻辑：
    获取当前焦点窗口 → 切换置顶状态 → 更新托盘图标 → 发送气泡通知
    """
    # 1. 获取当前焦点窗口
    hwnd, title = window_manager.get_foreground_window()

    # 2. hwnd 为 0 表示获取失败，直接返回
    if not hwnd:
        log.warning("on_hotkey_triggered: 未能获取焦点窗口，跳过")
        return

    # 3 & 4. 切换置顶状态，捕获权限错误
    try:
        new_state = window_manager.toggle_topmost(hwnd)
    except PermissionError:
        log.warning(f"权限不足，无法操作窗口: {title!r}")
        if _tray:
            _tray.notify("权限不足", "请以管理员身份运行")
        return
    except Exception as e:
        log.error(f"toggle_topmost 意外异常 hwnd={hwnd}: {e}")
        return

    # 5 & 6. 根据新状态更新集合并发送通知
    short_title = (title[:28] + "…") if len(title) > 28 else title

    if new_state:
        _managed_hwnds.add(hwnd)
        log.info(f"已置顶: hwnd={hwnd}  title={title!r}")
        if _tray:
            _tray.notify("已置顶 📌", short_title)
    else:
        _managed_hwnds.discard(hwnd)
        log.info(f"已取消置顶: hwnd={hwnd}  title={title!r}")
        if _tray:
            _tray.notify("已取消置顶", short_title)

    # 7. 根据是否还有置顶窗口切换托盘图标状态
    if _tray:
        _tray.update_icon(bool(_managed_hwnds))


# ════════════════════════════════════════════════
# 托盘回调
# ════════════════════════════════════════════════

def on_clear_all() -> None:
    """
    取消全部由本工具管理的置顶窗口。
    由托盘菜单「取消全部置顶」触发。
    """
    count = len(_managed_hwnds)
    if count == 0:
        log.info("on_clear_all: 当前无置顶窗口，跳过")
        return

    window_manager.clear_all_topmost(list(_managed_hwnds))
    _managed_hwnds.clear()

    if _tray:
        _tray.update_icon(False)
        _tray.notify("已取消全部置顶", "所有窗口恢复正常层级")

    log.info(f"on_clear_all: 已清除 {count} 个置顶窗口")


def on_quit() -> None:
    """
    退出前清理：取消所有置顶 → 停止快捷键监听。
    由托盘菜单「退出」触发，在 TrayApp.stop() 之前执行。
    """
    log.info("正在退出 TopMost Tool...")
    on_clear_all()
    hotkey_listener.stop()
    log.info("清理完成，程序退出")


# ════════════════════════════════════════════════
# 入口
# ════════════════════════════════════════════════

def main() -> None:
    global _tray

    log.info("TopMost Tool 启动中...")

    # ── 步骤 1：加载配置 ──────────────────────────
    try:
        cfg = config_manager.load()
    except Exception as e:
        log.error(f"配置加载失败，使用默认值: {e}")
        cfg = {}

    hotkey = cfg.get("hotkey", "ctrl+space")
    log.info(f"配置加载完毕，快捷键: {hotkey!r}")

    # ── 步骤 2：启动全局快捷键监听（后台线程）────
    try:
        hotkey_listener.start(hotkey, on_hotkey_triggered)
        log.info(f"快捷键监听已启动: {hotkey.upper()}")
    except Exception as e:
        log.error(f"快捷键监听启动失败: {e}")
        log.error("提示：keyboard 库需要管理员权限，请以管理员身份运行")
        sys.exit(1)

    # ── 步骤 3：初始化托盘并启动主循环（阻塞）────
    _tray = TrayApp(
        on_clear_all=on_clear_all,
        on_quit=on_quit,
    )

    log.info("TopMost Tool 已就绪，常驻系统托盘")
    log.info(f"按 {hotkey.upper()} 置顶 / 取消置顶当前焦点窗口")
    log.info("右键托盘图标可查看置顶窗口列表或退出程序")

    # run() 阻塞主线程直到用户点击「退出」
    _tray.run()


if __name__ == "__main__":
    main()
