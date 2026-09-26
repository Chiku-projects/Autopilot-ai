import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Optional

from app.agent.loop import AgentLoop, TaskResult
from app.ai.schemas import PlanStep

logger = logging.getLogger(__name__)


@dataclass
class LiveTask:
    task_id: str
    goal: str
    status: str = "running"  # running | awaiting_confirmation | completed | failed | cancelled
    pending_step: Optional[PlanStep] = None
    result: Optional[TaskResult] = None
    _confirm_event: threading.Event = field(default_factory=threading.Event)
    _confirm_decision: bool = False
    _loop: Optional[AgentLoop] = None


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, LiveTask] = {}

    def start_task(self, goal: str) -> str:
        task_id = str(uuid.uuid4())
        live = LiveTask(task_id=task_id, goal=goal)
        self._tasks[task_id] = live

        def confirm_callback(step: PlanStep) -> bool:
            live.pending_step = step
            live.status = "awaiting_confirmation"
            live._confirm_event.clear()
            live._confirm_event.wait()  # blocks the background thread here
            live.status = "running"
            live.pending_step = None
            return live._confirm_decision

        loop = AgentLoop(confirm_callback=confirm_callback)
        live._loop = loop

        def run_task():
            result = loop.run(goal)
            live.result = result
            live.status = result.status

        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        return task_id

    def get_task(self, task_id: str) -> Optional[LiveTask]:
        return self._tasks.get(task_id)

    def confirm(self, task_id: str, approve: bool) -> bool:
        live = self._tasks.get(task_id)
        if live is None or live.status != "awaiting_confirmation":
            return False
        live._confirm_decision = approve
        live._confirm_event.set()
        return True

    def cancel(self, task_id: str) -> bool:
        live = self._tasks.get(task_id)
        if live is None:
            return False
        if live._loop:
            live._loop.cancel()
        return True

    def list_tasks(self) -> list[LiveTask]:
        return list(self._tasks.values())


task_manager = TaskManager()