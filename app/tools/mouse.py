import logging
import pyautogui

from app.tools.schemas import ToolResult

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True  # move mouse to a screen corner to abort (Rule 10 safety net)


def _validate_coords(x: int, y: int) -> str | None:
    width, height = pyautogui.size()
    if not (0 <= x <= width) or not (0 <= y <= height):
        return f"Coordinates ({x}, {y}) out of screen bounds ({width}x{height})"
    return None


def click(x: int, y: int) -> ToolResult:
    error = _validate_coords(x, y)
    if error:
        return ToolResult(success=False, error=error)
    try:
        pyautogui.click(x, y)
        return ToolResult(success=True, data={"clicked": [x, y]})
    except Exception as e:
        logger.exception("click failed")
        return ToolResult(success=False, error=str(e))


def double_click(x: int, y: int) -> ToolResult:
    error = _validate_coords(x, y)
    if error:
        return ToolResult(success=False, error=error)
    try:
        pyautogui.doubleClick(x, y)
        return ToolResult(success=True, data={"double_clicked": [x, y]})
    except Exception as e:
        logger.exception("double_click failed")
        return ToolResult(success=False, error=str(e))


def move_mouse(x: int, y: int) -> ToolResult:
    error = _validate_coords(x, y)
    if error:
        return ToolResult(success=False, error=error)
    try:
        pyautogui.moveTo(x, y)
        return ToolResult(success=True, data={"moved_to": [x, y]})
    except Exception as e:
        logger.exception("move_mouse failed")
        return ToolResult(success=False, error=str(e))


def scroll(amount: int, direction: str = "down") -> ToolResult:
    if direction not in ("up", "down"):
        return ToolResult(success=False, error="direction must be 'up' or 'down'")
    try:
        signed_amount = amount if direction == "up" else -amount
        pyautogui.scroll(signed_amount)
        return ToolResult(success=True, data={"scrolled": signed_amount})
    except Exception as e:
        logger.exception("scroll failed")
        return ToolResult(success=False, error=str(e))