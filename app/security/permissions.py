import logging
from typing import Callable

from app.ai.schemas import PlanStep
from app.security.risk import RiskTier, classify_risk

logger = logging.getLogger(__name__)

# Signature: (step: PlanStep) -> bool  (True = approved, False = denied)
ConfirmCallback = Callable[[PlanStep], bool]

def default_cli_confirm(step: PlanStep) -> bool:
    print("\nAutoPilot wants to:")
    print(f"  {step.action}({step.arguments})")
    print(f"  Reason: {step.reason}")

    for _ in range(3):
        answer = input("Allow this action? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")

    print("No valid answer given — defaulting to deny.")
    return False
    print("\nAutoPilot wants to:")
    print(f"  {step.action}({step.arguments})")
    print(f"  Reason: {step.reason}")

    for _ in range(3):
        answer = input("Allow this action? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")

    print("No valid answer given — defaulting to deny.")
    return False


class PermissionGate:
    def __init__(self, confirm_callback: ConfirmCallback = default_cli_confirm):
        self._confirm_callback = confirm_callback

    def check(self, step: PlanStep) -> tuple[bool, str]:
        """Returns (allowed, reason)."""
        tier = classify_risk(step)

        if tier == RiskTier.BLOCKED:
            logger.warning("Step blocked by risk policy: %s(%s)", step.action, step.arguments)
            return False, f"Action '{step.action}' is blocked by policy in MVP"

        if tier == RiskTier.CONFIRM:
            approved = self._confirm_callback(step)
            if not approved:
                return False, "User denied confirmation"
            return True, "User approved"

        return True, "Safe — no confirmation required"