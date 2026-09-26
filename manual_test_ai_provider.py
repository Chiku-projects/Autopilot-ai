from app.ai.provider import get_ai_provider

provider = get_ai_provider()

fake_observation = {
    "active_window": {"title": "Desktop", "process_name": "explorer.exe"},
    "screen_width": 1920,
    "screen_height": 1080,
    "windows": [],
}

plan = provider.create_plan("Open Notepad and type Hello World.", fake_observation)
print(plan.model_dump_json(indent=2))
