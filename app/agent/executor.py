import logging
from typing import Callable

from app.ai.schemas import PlanStep
from app.tools.schemas import ToolResult
from app.tools import desktop, mouse, keyboard
from app.tools import desktop, mouse, keyboard, browser
from app.tools import desktop, mouse, keyboard, browser, credentials
from app.tools import desktop_whatsapp

# add to TOOL_DISPATCH:


logger = logging.getLogger(__name__)

# Explicit allowlist dispatch — the only actions the executor will ever run.
TOOL_DISPATCH: dict[str, Callable[..., ToolResult]] = {
    "open_app": lambda args: desktop.open_app(args["name"]),
    

# add to TOOL_DISPATCH:
    "whatsapp_open_chat": lambda args: desktop_whatsapp.whatsapp_open_chat(args["contact_name"]),
    "whatsapp_type_message": lambda args: desktop_whatsapp.whatsapp_type_message(args["message"]),
    "whatsapp_send_typed_message": lambda args: desktop_whatsapp.whatsapp_send_typed_message(),
    "close_app": lambda args: desktop.close_app(args["name"]),
    "focus_window": lambda args: desktop.focus_window(args["title"]),
     "voice_enter_credential": lambda args: credentials.voice_enter_credential(
            args.get("selector"), args.get("duration_seconds", 4.0)
        ),
    "click": lambda args: mouse.click(args["x"], args["y"]),
    "double_click": lambda args: mouse.double_click(args["x"], args["y"]),
    "move_mouse": lambda args: mouse.move_mouse(args["x"], args["y"]),
    "scroll": lambda args: mouse.scroll(args["amount"], args.get("direction", "down")),
    "type_text": lambda args: keyboard.type_text(args["text"]),
    "press_key": lambda args: keyboard.press_key(args["key"]),
    "hotkey": lambda args: keyboard.hotkey(args["keys"]),
     "browser_open": lambda args: browser.browser_open(args.get("url")),
    "browser_navigate": lambda args: browser.browser_navigate(args["url"]),
    "browser_click": lambda args: browser.browser_click(args["selector"]),
    "browser_type": lambda args: browser.browser_type(args["selector"], args["text"]),
    "browser_read_page": lambda args: browser.browser_read_page(),
}


def execute_step(step: PlanStep) -> ToolResult:
    handler = TOOL_DISPATCH.get(step.action)
    if handler is None:
        return ToolResult(success=False, error=f"Unknown action '{step.action}' — refusing to execute")
    try:
        return handler(step.arguments)
    except KeyError as e:
        return ToolResult(success=False, error=f"Missing required argument {e} for '{step.action}'")
    except Exception as e:
        logger.exception("execute_step failed for %s", step.action)
        return ToolResult(success=False, error=str(e))