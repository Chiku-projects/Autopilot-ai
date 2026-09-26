from app.observation.capture import observe
from app.tools.desktop import open_app

print(open_app("notepad"))

obs = observe(include_screenshot=True)
print("\nActive window:", obs.active_window)
print("Screen size:", obs.screen_width, "x", obs.screen_height)
print("Window count:", len(obs.windows))
print("Screenshot saved to:", obs.screenshot_path)
