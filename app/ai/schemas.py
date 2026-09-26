from typing import Any
from pydantic import BaseModel


class PlanStep(BaseModel):
    action: str
    arguments: dict[str, Any]
    reason: str


class Plan(BaseModel):
    goal: str
    steps: list[PlanStep]