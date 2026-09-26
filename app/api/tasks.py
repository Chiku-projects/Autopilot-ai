from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.task_manager import task_manager
from app.voice.stt import get_speech_provider

router = APIRouter()


class TaskCreateRequest(BaseModel):
    goal: str


class ConfirmRequest(BaseModel):
    approve: bool


@router.post("/tasks")
def create_task(req: TaskCreateRequest):
    task_id = task_manager.start_task(req.goal)
    return {"task_id": task_id}
@router.post("/voice/transcribe")
def transcribe_voice():
    provider = get_speech_provider()
    text = provider.record_and_transcribe(duration_seconds=5.0)
    return {"text": text}

@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    live = task_manager.get_task(task_id)
    if live is None:
        raise HTTPException(404, "Task not found")

    history = []
    if live.result:
        history = [
            {"action": s.action, "arguments": s.arguments, "reason": s.reason,
             "success": s.success, "explanation": s.explanation}
            for s in live.result.history
        ]

    return {
        "task_id": live.task_id,
        "goal": live.goal,
        "status": live.status,
        "pending_step": (
            {"action": live.pending_step.action, "arguments": live.pending_step.arguments,
             "reason": live.pending_step.reason}
            if live.pending_step else None
        ),
        "history": history,
    }


@router.post("/tasks/{task_id}/confirm")
def confirm_task(task_id: str, req: ConfirmRequest):
    ok = task_manager.confirm(task_id, req.approve)
    if not ok:
        raise HTTPException(400, "No pending confirmation for this task")
    return {"confirmed": req.approve}


@router.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    ok = task_manager.cancel(task_id)
    if not ok:
        raise HTTPException(404, "Task not found")
    return {"cancelled": True}