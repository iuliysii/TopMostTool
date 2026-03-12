"""
window_manager.py  —  模块 A：窗口枚举与置顶操作
依赖：pywin32 >= 311（支持 Python 3.10–3.14）

Python 3.14 说明：
  pywin32 311（2025-07 发布）已正式支持 Python 3.14 正式版。
  若安装失败请确认：
    1. Python 版本 >= 3.14.0 正式版（非 alpha/beta）
    2. pip install "pywin32>=311"
"""

import ctypes
import logging
import sys
from typing import Optional

# ── Python 版本检查 ──────────────────────────────
if sys.version_info < (3, 10):
    raise RuntimeError("TopMost Tool 需要 Python 3.10 或更高版本")

try:
    import win32con
    import win32gui
    import win32process
except ImportError as e:
    _v = sys.version_info
    raise ImportError(
        f"无法导入 pywin32（当前 Python {_v.major}.{_v.minor}.{_v.micro}）\n"
        f"请运行：pip install \"pywin32>=311\"\n"
        f"若使用 Python 3.14，请确认使用正式版（非 alpha/beta）\n"
        f"原始错误：{e}"
    ) from e

# ── 日志 ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[WM] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── Win32 常量 ───────────────────────────────────
HWND_TOPMOST   = -1
HWND_NOTOPMOST = -2
SWP_FLAGS      = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
WS_EX_TOPMOST  = win32con.WS_EX_TOPMOST


# ════════════════════════════════════════════════
# 内部工具
# ════════════════════════════════════════════════

def _is_admin() -> bool:
    """当前进程是否拥有管理员权限。"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _get_window_title(hwnd: int) -> str:
    """安全获取窗口标题，失败返回空字符串。"""
    try:
        return win32gui.GetWindowText(hwnd)
    except Exception:
        return ""


# ════════════════════════════════════════════════
# 公开接口
# ════════════════════════════════════════════════

def get_foreground_window() -> tuple[int, str]:
    """
    获取当前焦点窗口的句柄与标题。

    Returns:
        (hwnd, title)  —  hwnd=0 表示获取失败。
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            log.warning("GetForegroundWindow 返回空句柄")
            return 0, ""
        title = _get_window_title(hwnd)
        log.info(f"当前焦点窗口: hwnd={hwnd}  title={title!r}")
        return hwnd, title
    except Exception as e:
        log.error(f"get_foreground_window 异常: {e}")
        return 0, ""


def is_topmost(hwnd: int) -> bool:
    """
    判断窗口当前是否处于置顶状态。

    使用 GWL_EXSTYLE & WS_EX_TOPMOST 判断。
    """
    try:
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        return bool(ex_style & WS_EX_TOPMOST)
    except Exception as e:
        log.error(f"is_topmost 异常 hwnd={hwnd}: {e}")
        return False


def set_topmost(hwnd: int, on: bool) -> bool:
    """
    设置或取消窗口置顶。

    Args:
        hwnd: 目标窗口句柄。
        on:   True=置顶，False=取消置顶。

    Returns:
        True=操作成功，False=操作失败。

    Raises:
        PermissionError: 目标窗口属于更高权限进程。
    """
    if not hwnd:
        log.warning("set_topmost: hwnd 为空，跳过")
        return False

    insert_after = HWND_TOPMOST if on else HWND_NOTOPMOST
    action       = "置顶" if on else "取消置顶"
    title        = _get_window_title(hwnd)

    try:
        # pywin32 的 SetWindowPos 成功时返回 None（不抛异常即为成功）
        win32gui.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, SWP_FLAGS)
        log.info(f"{action}成功: hwnd={hwnd}  title={title!r}")
        return True

    except PermissionError:
        raise
    except Exception as e:
        log.error(f"set_topmost 异常 hwnd={hwnd}: {e}")
        if not _is_admin():
            raise PermissionError(
                f"无法操作窗口: {title!r}，请以管理员运行"
            ) from e
        return False


def toggle_topmost(hwnd: int) -> bool:
    """
    切换窗口的置顶状态（置顶 ↔ 取消置顶）。

    Returns:
        切换后的置顶状态：True=现在是置顶，False=现在是非置顶。

    Raises:
        PermissionError: 权限不足时向上抛出。
    """
    current = is_topmost(hwnd)
    target  = not current
    set_topmost(hwnd, target)  # 失败时向上 raise
    log.info(f"toggle_topmost: hwnd={hwnd}  {current} → {target}")
    return target


def get_topmost_windows() -> list[dict]:
    """
    枚举当前所有置顶窗口（仅返回可见且有标题的顶层窗口）。

    Returns:
        列表，每项为 {"hwnd": int, "title": str, "pid": int}
    """
    result: list[dict] = []

    def _callback(hwnd: int, _) -> None:
        try:
            # 只处理可见窗口
            if not win32gui.IsWindowVisible(hwnd):
                return
            # 必须有标题
            title = _get_window_title(hwnd)
            if not title:
                return
            # 检查 WS_EX_TOPMOST
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if not (ex_style & WS_EX_TOPMOST):
                return
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            result.append({"hwnd": hwnd, "title": title, "pid": pid})
        except Exception as e:
            log.debug(f"枚举窗口跳过 hwnd={hwnd}: {e}")

    try:
        win32gui.EnumWindows(_callback, None)
    except Exception as e:
        log.error(f"get_topmost_windows EnumWindows 失败: {e}")

    log.info(f"当前置顶窗口数量: {len(result)}")
    return result


def clear_all_topmost(managed_hwnds: list[int] | None = None) -> None:
    """
    取消所有置顶窗口。

    Args:
        managed_hwnds: 若提供，仅取消这些句柄；
                       若为 None，则枚举全部置顶窗口并取消。
    """
    targets = managed_hwnds if managed_hwnds is not None \
              else [w["hwnd"] for w in get_topmost_windows()]

    success = 0
    for hwnd in targets:
        try:
            set_topmost(hwnd, False)
            success += 1
        except PermissionError as e:
            # 权限不足时记录警告，继续处理其他窗口
            log.warning(f"clear_all_topmost 跳过受限窗口 hwnd={hwnd}: {e}")
        except Exception as e:
            log.error(f"clear_all_topmost 异常 hwnd={hwnd}: {e}")

    log.info(f"clear_all_topmost 完成: {success}/{len(targets)} 个窗口已取消置顶")


# ════════════════════════════════════════════════
# __main__ 自测块
# 使用方式：python window_manager.py
# 步骤：运行后 2 秒内点击你想置顶的目标窗口
# ════════════════════════════════════════════════

if __name__ == "__main__":
    import time

    print("=" * 55)
    print("  window_manager.py  自测")
    print("  请在 2 秒内点击你想置顶的目标窗口...")
    print("=" * 55)
    time.sleep(2)

    # ── 步骤 1：获取焦点窗口 ──────────────────────
    hwnd, title = get_foreground_window()
    if not hwnd:
        print("[ERROR] 未能获取焦点窗口，请重试")
        sys.exit(1)

    print(f"\n[目标窗口]")
    print(f"  hwnd  = {hwnd}")
    print(f"  title = {title!r}")
    print(f"  置顶前状态: is_topmost = {is_topmost(hwnd)}")

    # ── 步骤 2：置顶 ──────────────────────────────
    print("\n[操作] 正在置顶...")
    try:
        new_state = toggle_topmost(hwnd)
        print(f"  置顶后状态: is_topmost = {new_state}  ✅")
    except PermissionError as e:
        print(f"  [PermissionError] {e}")
        print("  提示：请以管理员身份重新运行此脚本")
        sys.exit(1)

    # ── 步骤 3：等待 3 秒，期间窗口应始终在最前 ──
    print("\n[等待] 置顶中，3 秒后自动取消...")
    for i in range(3, 0, -1):
        print(f"  {i}...", end="\r")
        time.sleep(1)

    # ── 步骤 4：取消置顶 ──────────────────────────
    print("\n[操作] 正在取消置顶...")
    try:
        new_state = toggle_topmost(hwnd)
        print(f"  取消后状态: is_topmost = {new_state}  ✅")
    except PermissionError as e:
        print(f"  [PermissionError] {e}")

    # ── 步骤 5：打印当前所有置顶窗口 ─────────────
    print("\n[枚举] 当前所有置顶窗口:")
    topmost_list = get_topmost_windows()
    if not topmost_list:
        print("  （无置顶窗口）")
    else:
        for w in topmost_list:
            print(f"  hwnd={w['hwnd']:>8}  pid={w['pid']:>6}  title={w['title']!r}")

    print("\n自测完成 ✅")
