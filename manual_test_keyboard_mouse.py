import time
from app.tools.desktop import open_app, close_app, focus_window
from app.tools.keyboard import type_text, press_key, hotkey
from app.tools.mouse import click, move_mouse

print(open_app("notepad"))
time.sleep(1.5)
print(focus_window("Notepad"))
time.sleep(0.5)

print(type_text("Hello AutoPilot"))
time.sleep(0.5)

print(press_key("enter"))
print(type_text("Second line"))
time.sleep(0.5)

print(hotkey(["ctrl", "a"]))  # select all
time.sleep(0.5)

print(close_app("notepad"))