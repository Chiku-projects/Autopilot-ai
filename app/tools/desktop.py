import os
import subprocess
import time
import logging

import psutil
from pywinauto import Desktop
from pywinauto.application import Application
from pywinauto import findwindows

from app.tools.schemas import ToolResult, WindowInfo

logger = logging.getLogger(__name__)

# MVP: a small known-apps map. Extend as needed; unknown names fall back
# to treating the input as a literal executable/command.
APP_COMMANDS = {
    "notepad": "notepad.exe",
    "chrome": "chrome.exe",
    "vs code": "code",
    "vscode": "code",
    "explorer": "explorer.exe",
    "calculator": "calc.exe",
    "whatsapp": "whatsapp:",       # WhatsApp registers a URI protocol handler
    "spotify": "spotify:",
    "instagram": "instagram:",
    "twitter": "twitter:",
}

# Common user folders the planner can reference by plain name instead of
# a literal filesystem path.
KNOWN_FOLDERS = {
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
}


def _resolve_command(name: str) -> str:
    return APP_COMMANDS.get(name.strip().lower(), name)


def open_app(name: str) -> ToolResult:
    lowered = name.strip().lower()

    # folder-path shortcut — opens a known user folder in File Explorer
    if lowered in KNOWN_FOLDERS:
        try:
            folder_path = KNOWN_FOLDERS[lowered]
            subprocess.Popen(f'explorer "{folder_path}"')
            time.sleep(1.0)
            return ToolResult(success=True, data={"launched": folder_path})
        except Exception as e:
            logger.exception("open_app failed opening folder %s", name)
            return ToolResult(success=False, error=str(e))

    command = _resolve_command(name)
    try:
        if command.endswith(":"):
            # URI-scheme app (WhatsApp, Spotify, etc.) — must go through
            # the shell's URI handler, not run as a literal executable.
            subprocess.Popen(f'start "" "{command}"', shell=True)
        else:
            subprocess.Popen(command, shell=True)
        time.sleep(1.5)
        return ToolResult(success=True, data={"launched": command})
    except Exception as e:
        logger.exception("open_app failed for %s", name)
        return ToolResult(success=False, error=str(e))


def close_app(name: str) -> ToolResult:
    target = name.strip().lower()
    closed = []
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            proc_name = (proc.info["name"] or "").lower()
            if target in proc_name:
                proc.terminate()
                closed.append(proc.info["name"])
        if not closed:
            return ToolResult(success=False, error=f"No running process matching '{name}'")
        return ToolResult(success=True, data={"closed": closed})
    except Exception as e:
        logger.exception("close_app failed for %s", name)
        return ToolResult(success=False, error=str(e))


def get_windows() -> ToolResult:
    try:
        windows = []
        for w in Desktop(backend="uia").windows():
            try:
                windows.append(
                    WindowInfo(
                        title=w.window_text(),
                        process_name=psutil.Process(w.process_id()).name(),
                        pid=w.process_id(),
                        is_minimized=w.is_minimized(),
                        is_active=w.is_active(),
                    )
                )
            except Exception:
                continue  # skip windows we can't introspect
        return ToolResult(success=True, data=[w.model_dump() for w in windows])
    except Exception as e:
        logger.exception("get_windows failed")
        return ToolResult(success=False, error=str(e))


def focus_window(title: str, retries: int = 5, delay: float = 1.5) -> ToolResult:
    last_error = f"No window matching '{title}'"
    for attempt in range(retries):
        try:
            handles = findwindows.find_windows(title_re=f".*{title}.*", backend="uia")
            if not handles:
                last_error = f"No window matching '{title}'"
                time.sleep(delay)
                continue

            def pid_create_time(h):
                try:
                    app = Application(backend="uia").connect(handle=h)
                    return psutil.Process(app.top_window().process_id()).create_time()
                except Exception:
                    return -1  # bad/windowless handle — deprioritize, don't crash

            best_handle = max(handles, key=pid_create_time)

            app = Application(backend="uia").connect(handle=best_handle)
            win = app.top_window()
            win.set_focus()
            return ToolResult(success=True, data={"focused": win.window_text()})
        except Exception as e:
            last_error = str(e)
            logger.warning("focus_window attempt %d failed for %s: %s", attempt + 1, title, e)
            time.sleep(delay)

    logger.exception("focus_window failed for %s after %d attempts", title, retries)
    return ToolResult(success=False, error=last_error)