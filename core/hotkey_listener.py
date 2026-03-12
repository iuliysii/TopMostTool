"""
hotkey_listener.py  —  模块 B：全局快捷键监听
依赖：keyboard >= 0.13.5

注意：keyboard 库在 Windows 下需要管理员权限才能注册全局钩子。
"""

import logging
import threading
import time
from typing import Callable, Optional

try:
    import keyboard
except ImportError as e:
    raise ImportError(
        "无法导入 keyboard 库\n"
        "请运行：pip install keyboard>=0.13.5\n"
        f"原始错误：{e}"
    ) from e

# ── 日志 ─────────────────────────────────────────
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# ════════════════════════════════════════════════
# HotkeyListener 类
# ════════════════════════════════════════════════

class HotkeyListener:
    """
    在后台 daemon 线程中监听全局快捷键。
    触发时在独立子线程中执行回调，不阻塞钩子线程。
    支持运行时 update_hotkey() 热更新，无需重启。
    """

    def __init__(self) -> None:
        self._hotkey:   Optional[str]             = None
        self._callback: Optional[Callable]         = None
        self._thread:   Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock       = threading.Lock()

    # ── 公开接口 ──────────────────────────────────

    @property
    def hotkey(self) -> Optional[str]:
        return self._hotkey

    def start(self, hotkey: str, callback: Callable) -> None:
        """
        启动后台监听线程并注册快捷键。

        Args:
            hotkey:   快捷键字符串，如 'ctrl+space'（大小写均可）。
            callback: 快捷键触发时调用的无参函数。
        """
        with self._lock:
            if self._thread and self._thread.is_alive():
                log.warning("HotkeyListener 已在运行，请先调用 stop()")
                return

            self._hotkey   = hotkey.lower().strip()
            self._callback = callback
            self._stop_event.clear()

            self._thread = threading.Thread(
                target=self._listen_loop,
                name="HotkeyListenerThread",
                daemon=True,
            )
            self._thread.start()
            log.info(f"快捷键监听已启动: {self._hotkey!r}")

    def stop(self) -> None:
        """停止监听线程并注销快捷键钩子。"""
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                log.debug("HotkeyListener 未在运行，无需 stop")
                return
            self._stop_event.set()
            self._unregister()
        # 等待线程退出（最多 2 秒），不在锁内等避免死锁
        if self._thread:
            self._thread.join(timeout=2.0)
        log.info("快捷键监听已停止")

    def update_hotkey(self, new_hotkey: str) -> None:
        """
        热更新快捷键，无需重启监听线程。

        Args:
            new_hotkey: 新的快捷键字符串。
        """
        new_hotkey = new_hotkey.lower().strip()
        with self._lock:
            old = self._hotkey
            self._unregister()          # 先注销旧钩子
            self._hotkey = new_hotkey
            self._register()            # 再注册新钩子
        log.info(f"快捷键已更新: {old!r} → {new_hotkey!r}")

    # ── 内部实现 ──────────────────────────────────

    def _register(self) -> None:
        """注册当前快捷键到 keyboard 钩子（调用方需持有 _lock）。"""
        if not self._hotkey or not self._callback:
            return
        try:
            keyboard.add_hotkey(
                self._hotkey,
                self._on_triggered,
                suppress=False,
            )
            log.debug(f"已注册快捷键: {self._hotkey!r}")
        except Exception as e:
            log.error(f"注册快捷键失败 {self._hotkey!r}: {e}")

    def _unregister(self) -> None:
        """注销当前快捷键钩子（调用方需持有 _lock）。"""
        if not self._hotkey:
            return
        try:
            keyboard.remove_hotkey(self._hotkey)
            log.debug(f"已注销快捷键: {self._hotkey!r}")
        except Exception as e:
            # 钩子不存在时 keyboard 会抛异常，属正常情况，只记录 debug
            log.debug(f"注销快捷键时忽略异常 {self._hotkey!r}: {e}")

    def _on_triggered(self) -> None:
        """
        键盘钩子回调（在 keyboard 内部线程中被调用）。
        立即派发到新的 daemon 子线程执行 callback，不阻塞钩子线程。
        """
        log.info(f"快捷键触发: {self._hotkey!r}")
        threading.Thread(
            target=self._safe_callback,
            name="HotkeyCallbackThread",
            daemon=True,
        ).start()

    def _safe_callback(self) -> None:
        """安全执行用户回调，捕获所有异常避免子线程崩溃。"""
        try:
            if self._callback:
                self._callback()
        except Exception as e:
            log.error(f"快捷键回调执行异常: {e}")

    def _listen_loop(self) -> None:
        """
        后台监听线程主循环：
        注册快捷键后阻塞等待 stop_event，触发后注销并退出。
        """
        with self._lock:
            self._register()
        # 阻塞直到 stop() 设置 stop_event
        self._stop_event.wait()
        # stop() 已在外部调用 _unregister()，这里只做日志
        log.debug("listen_loop 退出")


# ════════════════════════════════════════════════
# 模块级单例便捷函数
# ════════════════════════════════════════════════

_listener: Optional[HotkeyListener] = None


def start(hotkey: str, callback: Callable) -> None:
    """模块级便捷函数：创建单例并启动监听。"""
    global _listener
    _listener = HotkeyListener()
    _listener.start(hotkey, callback)


def stop() -> None:
    """模块级便捷函数：停止单例监听。"""
    global _listener
    if _listener:
        _listener.stop()
        _listener = None


def update_hotkey(new_hotkey: str) -> None:
    """模块级便捷函数：热更新单例快捷键。"""
    if _listener:
        _listener.update_hotkey(new_hotkey)
    else:
        log.warning("update_hotkey: 监听器未启动，忽略")


# ════════════════════════════════════════════════
# __main__ 自测块
# 使用方式：python hotkey_listener.py
# - 按 Ctrl+Space 触发计数
# - 5 秒后自动切换为 Ctrl+F9
# - 按 Esc 退出
# ════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[HL] %(levelname)s %(message)s",
    )

    trigger_count = 0
    _exit_event   = threading.Event()

    def on_hotkey():
        global trigger_count
        trigger_count += 1
        print(f"  触发！第 {trigger_count} 次", flush=True)

    def on_esc():
        print("\n  [Esc] 收到退出信号...")
        _exit_event.set()

    print("=" * 55)
    print("  hotkey_listener.py  自测")
    print("  按 Ctrl+Space 触发计数")
    print("  5 秒后自动切换为 Ctrl+F9")
    print("  按 Esc 退出")
    print("=" * 55)

    # 注册 Ctrl+Space
    start("ctrl+space", on_hotkey)
    print(f"\n[已注册] ctrl+space，监听中...\n")

    # 注册 Esc 退出（直接用 keyboard，不走 HotkeyListener）
    keyboard.add_hotkey("esc", on_esc)

    # 后台线程：5 秒后自动切换快捷键
    def _auto_switch():
        time.sleep(5)
        if not _exit_event.is_set():
            update_hotkey("ctrl+f9")
            print("\n  快捷键已切换为 ctrl+f9\n", flush=True)

    threading.Thread(target=_auto_switch, daemon=True).start()

    # 主线程阻塞等待退出信号（不调用 keyboard.wait()）
    _exit_event.wait()

    # 清理
    stop()
    try:
        keyboard.remove_hotkey("esc")
    except Exception:
        pass

    print(f"\n自测完成，共触发 {trigger_count} 次 ✅")
    sys.exit(0)
