import logging
import pyautogui

from app.tools.schemas import ToolResult

logger = logging.getLogger(__name__)

# MVP allowlist — prevents an LLM from passing arbitrary/garbage key names
# straight to pyautogui. Extend as real needs arise.
VALID_KEYS = {
    "enter", "tab", "esc", "escape", "backspace", "delete", "space",
    "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
    "ctrl", "alt", "shift", "win",
    *[f"f{i}" for i in range(1, 13)],
    *[chr(c) for c in range(ord("a"), ord("z") + 1)],
    *[str(d) for d in range(10)],
}


def type_text(text: str) -> ToolResult:
    try:
        pyautogui.write(text, interval=0.02)
        return ToolResult(success=True, data={"typed_chars": len(text)})
    except Exception as e:
        logger.exception("type_text failed")
        return ToolResult(success=False, error=str(e))


def press_key(key: str) -> ToolResult:
    key = key.strip().lower()
    if key not in VALID_KEYS:
        return ToolResult(success=False, error=f"'{key}' is not an allowed key")
    try:
        pyautogui.press(key)
        return ToolResult(success=True, data={"pressed": key})
    except Exception as e:
        logger.exception("press_key failed")
        return ToolResult(success=False, error=str(e))


def hotkey(keys: list[str]) -> ToolResult:
    normalized = [k.strip().lower() for k in keys]
    invalid = [k for k in normalized if k not in VALID_KEYS]
    if invalid:
        return ToolResult(success=False, error=f"Invalid keys: {invalid}")
    try:
        pyautogui.hotkey(*normalized)
        return ToolResult(success=True, data={"hotkey": normalized})
    except Exception as e:
        logger.exception("hotkey failed")
        return ToolResult(success=False, error=str(e))