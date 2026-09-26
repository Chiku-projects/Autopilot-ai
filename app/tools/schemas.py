from typing import Any, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class WindowInfo(BaseModel):
    title: str
    process_name: str
    pid: int
    is_minimized: bool
    is_active: bool


class Observation(BaseModel):
    active_window: Optional[WindowInfo] = None
    screen_width: int
    screen_height: int
    windows: list[WindowInfo] = []
    screenshot_path: Optional[str] = None