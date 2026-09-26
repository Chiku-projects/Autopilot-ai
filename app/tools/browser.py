import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Playwright

from app.tools.schemas import ToolResult

logger = logging.getLogger(__name__)
USER_DATA_DIR = Path("data/browser_profile")  # or your fixed version
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
print(">>> USER_DATA_DIR =", USER_DATA_DIR.resolve())
_playwright: Playwright | None = None
_context = None
_page: Page | None = None


def _ensure_started() -> str | None:
    global _playwright, _context, _page
    if _page is not None:
        return None
    try:
        _playwright = sync_playwright().start()
        _context = _playwright.chromium.launch_persistent_context(
            str(USER_DATA_DIR),
            headless=False,
            channel="chrome",  # use real installed Chrome instead of bundled Chromium
        )
        _page = _context.pages[0] if _context.pages else _context.new_page()
        return None
    except Exception as e:
        logger.exception("Failed to start browser")
        return str(e)

def browser_open(url: str | None = None) -> ToolResult:
    error = _ensure_started()
    if error:
        return ToolResult(success=False, error=error)
    try:
        if url:
            _page.goto(url, wait_until="domcontentloaded")
        return ToolResult(success=True, data={"url": _page.url})
    except Exception as e:
        logger.exception("browser_open failed")
        return ToolResult(success=False, error=str(e))


def browser_navigate(url: str) -> ToolResult:
    error = _ensure_started()
    if error:
        return ToolResult(success=False, error=error)
    try:
        _page.goto(url, wait_until="domcontentloaded")
        return ToolResult(success=True, data={"url": _page.url, "title": _page.title()})
    except Exception as e:
        logger.exception("browser_navigate failed")
        return ToolResult(success=False, error=str(e))


def browser_click(selector: str) -> ToolResult:
    if _page is None:
        return ToolResult(success=False, error="Browser not open — call browser_open first")
    try:
        _page.click(selector, timeout=5000)
        return ToolResult(success=True, data={"clicked": selector})
    except Exception as e:
        logger.exception("browser_click failed")
        return ToolResult(success=False, error=str(e))


def browser_type(selector: str, text: str) -> ToolResult:
    if _page is None:
        return ToolResult(success=False, error="Browser not open — call browser_open first")
    try:
        _page.fill(selector, text, timeout=5000)
        return ToolResult(success=True, data={"typed_into": selector})
    except Exception as e:
        logger.exception("browser_type failed")
        return ToolResult(success=False, error=str(e))


def browser_read_page() -> ToolResult:
    if _page is None:
        return ToolResult(success=False, error="Browser not open — call browser_open first")
    try:
        headings = _page.locator("h1, h2, h3").all_inner_texts()
        return ToolResult(success=True, data={
            "url": _page.url,
            "title": _page.title(),
            "headings": headings[:10],
        })
    except Exception as e:
        logger.exception("browser_read_page failed")
        return ToolResult(success=False, error=str(e))


def browser_close() -> ToolResult:
    global _playwright, _context, _page
    try:
        if _context:
            _context.close()
        if _playwright:
            _playwright.stop()
        _playwright = _context = _page = None
        return ToolResult(success=True, data={"closed": True})
    except Exception as e:
        logger.exception("browser_close failed")
        return ToolResult(success=False, error=str(e))