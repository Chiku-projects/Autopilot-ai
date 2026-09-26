from enum import Enum
import re

from app.ai.schemas import PlanStep


class RiskTier(str, Enum):
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCKED = "blocked"


# Keywords that escalate a step to CONFIRM when found in its arguments
# (selectors, text, titles) — crude but effective for MVP.
CONFIRM_KEYWORDS = re.compile(
    r"\b(send|submit|post|buy|purchase|pay|checkout|delete message|confirm order)\b",
    re.IGNORECASE,
)

# Action names that are always CONFIRM regardless of arguments.
ALWAYS_CONFIRM_ACTIONS = set()  # e.g. add "browser_type" selectors matched below instead

# Action names that are always BLOCKED in MVP — no confirmation path yet.
ALWAYS_BLOCKED_ACTIONS = {
    "close_app",  # closing arbitrary apps can lose unsaved work — confirm-worthy at minimum;
                  # MVP blocks it outright since we have no "are you sure" UI yet
}

HIGH_RISK_KEYWORDS = re.compile(
    r"\b(delete|format|uninstall|regedit|rm -rf|del /|shutdown|diskpart|"
    r"install|admin|administrator|password|credit card|bank)\b",
    re.IGNORECASE,
)


def classify_risk(step: PlanStep) -> RiskTier:
    arg_text = " ".join(str(v) for v in step.arguments.values())

    if step.action in ALWAYS_BLOCKED_ACTIONS:
        return RiskTier.BLOCKED
    if step.action == "whatsapp_send_typed_message":
        return RiskTier.CONFIRM

    if step.action == "voice_enter_credential":
        return RiskTier.CONFIRM  # not SAFE — this is still login/credential entry,
                                  # worth a heads-up pause before recording starts 

    if HIGH_RISK_KEYWORDS.search(arg_text) or HIGH_RISK_KEYWORDS.search(step.action):
        return RiskTier.BLOCKED

    if step.action in ALWAYS_CONFIRM_ACTIONS or CONFIRM_KEYWORDS.search(arg_text):
        return RiskTier.CONFIRM

    # browser_click/browser_type on anything not caught above is SAFE for MVP —
    # deliberately permissive default, tightened later as real usage reveals gaps
    return RiskTier.SAFE