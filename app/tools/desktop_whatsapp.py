import logging
import time

from app.tools.schemas import ToolResult
from app.tools.desktop import open_app, focus_window
from app.tools.mouse import click
from app.tools.keyboard import type_text, press_key, hotkey
from app.observation.capture import take_screenshot

logger = logging.getLogger(__name__)

# Calibrated for this machine's WhatsApp Desktop layout, maximized window.
SEARCH_BOX = (277, 123)
MESSAGE_BOX = (1150, 981)


def whatsapp_open_chat(contact_name: str) -> ToolResult:
    """Opens WhatsApp, maximizes it for consistent layout, clears any
    existing search text, and opens the given contact's chat using
    keyboard navigation (not a coordinate click on the result) so the
    exact result-list position never matters."""
    try:
        open_app("whatsapp")
        time.sleep(2)
        focus_window("WhatsApp")
        time.sleep(1)

        # maximize for consistent geometry every run
        hotkey(["win", "up"])
        time.sleep(0.5)

        # clear any leftover search text before typing new query
        click(*SEARCH_BOX)
        time.sleep(0.3)
        hotkey(["ctrl", "a"])
        press_key("backspace")
        time.sleep(0.3)

        type_text(contact_name)
        time.sleep(1.5)

        # keyboard-select the top result — no coordinate guessing
        press_key("down")
        time.sleep(0.2)
        press_key("enter")
        time.sleep(1.5)

        screenshot = take_screenshot()
        return ToolResult(success=True, data={
            "opened_search_for": contact_name,
            "screenshot": screenshot.data.get("path") if screenshot.success else None,
        })
    except Exception as e:
        logger.exception("whatsapp_open_chat failed")
        return ToolResult(success=False, error=str(e))


def whatsapp_type_message(message: str) -> ToolResult:
    """Types a message into the currently-open chat's message box.
    Deliberately does NOT press Enter/send — that is a separate,
    explicit step so a screenshot can be reviewed first."""
    try:
        click(*MESSAGE_BOX)
        time.sleep(0.3)
        type_text(message)
        time.sleep(0.3)

        screenshot = take_screenshot()
        return ToolResult(success=True, data={
            "typed": True,
            "screenshot": screenshot.data.get("path") if screenshot.success else None,
        })
    except Exception as e:
        logger.exception("whatsapp_type_message failed")
        return ToolResult(success=False, error=str(e))


def whatsapp_send_typed_message() -> ToolResult:
    """Presses Enter to actually send whatever is currently typed in the
    message box. This is a separate action specifically so it can be
    gated behind confirmation — never bundled with typing."""
    try:
        press_key("enter")
        return ToolResult(success=True, data={"sent": True})
    except Exception as e:
        logger.exception("whatsapp_send_typed_message failed")
        return ToolResult(success=False, error=str(e))