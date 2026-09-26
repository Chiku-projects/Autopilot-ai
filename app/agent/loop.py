import logging
import time
import uuid
from dataclasses import dataclass, field

from app.ai.provider import get_ai_provider
from app.observation.capture import observe
from app.agent.executor import execute_step
from app.agent.verifier import verify_step
from app.security.permissions import PermissionGate

logger = logging.getLogger(__name__)

MAX_STEPS = 15
MAX_RETRIES_PER_STEP = 2
TIMEOUT_SECONDS = 120


@dataclass
class StepRecord:
    action: str
    arguments: dict
    reason: str
    success: bool
    explanation: str


@dataclass
class TaskResult:
    task_id: str
    goal: str
    status: str  # "completed" | "failed" | "cancelled" | "max_steps_exceeded" | "timeout"
    history: list[StepRecord] = field(default_factory=list)


class AgentLoop:
    def __init__(self, confirm_callback=None):
        self._provider = get_ai_provider()
        self._cancelled = False
        self._gate = PermissionGate(confirm_callback) if confirm_callback else PermissionGate()

    def cancel(self):
        self._cancelled = True

    def run(self, goal: str) -> TaskResult:
        task_id = str(uuid.uuid4())
        history: list[StepRecord] = []
        start_time = time.time()

        current_observation = observe()
        plan = self._provider.create_plan(goal, current_observation.model_dump())
        logger.info("Plan created with %d steps for goal: %s", len(plan.steps), goal)

        step_index = 0
        while step_index < len(plan.steps):
            if self._cancelled:
                return TaskResult(task_id, goal, "cancelled", history)

            if time.time() - start_time > TIMEOUT_SECONDS:
                return TaskResult(task_id, goal, "timeout", history)

            if len(history) >= MAX_STEPS:
                return TaskResult(task_id, goal, "max_steps_exceeded", history)

            step = plan.steps[step_index]

            allowed, permission_reason = self._gate.check(step)
            if not allowed:
                history.append(StepRecord(
                    action=step.action,
                    arguments=step.arguments,
                    reason=step.reason,
                    success=False,
                    explanation=f"Permission denied: {permission_reason}",
                ))
                return TaskResult(task_id, goal, "failed", history)

            retries = 0
            success = False
            explanation = ""

            while retries <= MAX_RETRIES_PER_STEP and not success:
                before = current_observation
                tool_result = execute_step(step)
                time.sleep(0.5)  # let the OS/app settle before observing
                after = observe()
                success, explanation = verify_step(step, tool_result, before, after)
                current_observation = after

                if not success:
                    retries += 1
                    logger.warning("Step '%s' failed (attempt %d): %s", step.action, retries, explanation)

            history.append(StepRecord(
                action=step.action,
                arguments=step.arguments,
                reason=step.reason,
                success=success,
                explanation=explanation,
            ))

            if not success:
                return TaskResult(task_id, goal, "failed", history)

            step_index += 1

        return TaskResult(task_id, goal, "completed", history)