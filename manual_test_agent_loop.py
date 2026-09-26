from app.agent.loop import AgentLoop
from app.tools import windows
print(windows.open_app("WhatsApp"))
loop = AgentLoop()
result = loop.run(
    "Open the WhatsApp desktop application (not the web browser version) "
    "and send a message saying 'hi' to [pussycat]."
)

print(result.status)
for s in result.history:
    print(s.action, s.arguments, s.success, s.explanation)