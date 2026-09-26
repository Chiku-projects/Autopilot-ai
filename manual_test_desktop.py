from app.tools.desktop import open_app, close_app, get_windows, focus_window
from app.tools.desktop import open_app
print(open_app("downloads"))
print("Opening Notepad...")
print(open_app("notepad"))

print("\nListing windows...")
result = get_windows()
for w in result.data:
    print(w)

print("\nFocusing Notepad...")
print(focus_window("Notepad"))

print("\nClosing Notepad...")
print(close_app("notepad"))