import requests

BASE_URL = "http://localhost:8080/api/v1"


def create_task(goal: str) -> str:
    r = requests.post(f"{BASE_URL}/tasks", json={"goal": goal})
    r.raise_for_status()
    return r.json()["task_id"]


def get_task(task_id: str) -> dict:
    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    r.raise_for_status()
    return r.json()


def confirm_task(task_id: str, approve: bool) -> None:
    requests.post(f"{BASE_URL}/tasks/{task_id}/confirm", json={"approve": approve})


def cancel_task(task_id: str) -> None:
    requests.post(f"{BASE_URL}/tasks/{task_id}/cancel")