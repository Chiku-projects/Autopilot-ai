import logging
import time
from pathlib import Path
import win32gui
import win32process
import mss
import pyautogui
from pywinauto import Desktop

from app.tools.schemas import ToolResult, WindowInfo, Observation
from app.tools.desktop import get_windows

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path("data/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def get_screen_size() -> ToolResult:
    try:
        width, height = pyautogui.size()
        return ToolResult(success=True, data={"width": width, "height": height})
    except Exception as e:
        logger.exception("get_screen_size failed")
        return ToolResult(success=False, error=str(e))





def get_active_window() -> ToolResult:
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        import psutil
        process_name = psutil.Process(pid).name()

        info = WindowInfo(
            title=title,
            process_name=process_name,
            pid=pid,
            is_minimized=bool(win32gui.IsIconic(hwnd)),
            is_active=True,
        )
        return ToolResult(success=True, data=info.model_dump())
    except Exception as e:
        logger.exception("get_active_window failed")
        return ToolResult(success=False, error=str(e))
def take_screenshot() -> ToolResult:
    try:
        path = SCREENSHOT_DIR / f"screen_{int(time.time() * 1000)}.png"
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # primary monitor
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=str(path))
        return ToolResult(success=True, data={"path": str(path)})
    except Exception as e:
        logger.exception("take_screenshot failed")
        return ToolResult(success=False, error=str(e))


def observe(include_screenshot: bool = False) -> Observation:
    """Single structured snapshot of current computer state.
    Cheap by default; pass include_screenshot=True only when visual
    grounding is actually needed (see Phase 0 §6 strategy)."""
    size_result = get_screen_size()
    active_result = get_active_window()
    windows_result = get_windows()

    screenshot_path = None
    if include_screenshot:
        shot_result = take_screenshot()
        if shot_result.success:
            screenshot_path = shot_result.data["path"]

    return Observation(
        active_window=WindowInfo(**active_result.data) if active_result.success else None,
        screen_width=size_result.data["width"] if size_result.success else 0,
        screen_height=size_result.data["height"] if size_result.success else 0,
        windows=[WindowInfo(**w) for w in windows_result.data] if windows_result.success else [],
        screenshot_path=screenshot_path,
    )