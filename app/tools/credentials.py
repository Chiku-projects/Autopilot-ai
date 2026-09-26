import logging

from app.tools.schemas import ToolResult
from app.tools import browser, keyboard
from app.voice.stt import get_speech_provider

logger = logging.getLogger(__name__)


def voice_enter_credential(selector: str | None = None, duration_seconds: float = 4.0) -> ToolResult:
    """Records a short voice clip on the spot, transcribes it, and types
    the result immediately into the given field (browser selector) or the
    currently focused field (selector=None, for desktop apps). The
    transcribed value is never returned, logged, or stored anywhere —
    it exists only inside this function call."""
    provider = get_speech_provider()
    try:
        value = provider.record_and_transcribe(duration_seconds=duration_seconds)
    except Exception as e:
        logger.exception("voice_enter_credential: recording/transcription failed")
        return ToolResult(success=False, error=f"Voice capture failed: {e}")

    if not value:
        return ToolResult(success=False, error="Heard nothing — please try again")

    if selector:
        result = browser.browser_type(selector, value)
    else:
        result = keyboard.type_text(value)

    # deliberately do NOT include `value` in the returned data
    del value

    if result.success:
        return ToolResult(success=True, data={"filled": selector or "focused field"})
    return ToolResult(success=False, error="Failed to type captured credential")