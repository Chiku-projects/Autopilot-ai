from app.tools.schemas import Observation, ToolResult
from app.ai.schemas import PlanStep


def verify_step(step: PlanStep, tool_result: ToolResult, before: Observation, after: Observation) -> tuple[bool, str]:
    """Rule-based verification. Returns (success, explanation)."""
    if not tool_result.success:
        return False, f"Tool reported failure: {tool_result.error}"

    if step.action == "open_app":
        target = step.arguments.get("name", "").lower()
        matched = any(target in w.process_name.lower() or target in w.title.lower() for w in after.windows)
        if not matched:
            return False, f"No window found matching '{target}' after open_app"
        return True, f"Window matching '{target}' found after open_app"

    if step.action == "focus_window":
        title = step.arguments.get("title", "").lower()
        if after.active_window and title in after.active_window.title.lower():
            return True, "Active window matches focus target"
        return False, "Active window does not match focus target after focus_window"

    if step.action in ("close_app",):
        target = step.arguments.get("name", "").lower()
        still_open = any(target in w.process_name.lower() for w in after.windows)
        if still_open:
            return False, f"'{target}' still appears in window list after close_app"
        return True, f"'{target}' no longer found after close_app"

    # For actions with no strong observable signature yet (type_text, click, etc.),
    # MVP trusts tool_result.success. This is a known limitation — flagged, not fixed
    # here; Phase 14 (Error Recovery) is where this gets smarter.
    return True, "No specific verification rule for this action; trusting tool result"