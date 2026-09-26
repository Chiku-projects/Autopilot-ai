from app.agent.loop import AgentLoop
from app.tools.browser import browser_close

loop = AgentLoop()
result = loop.run("Open a browser and search Bing for FastAPI documentation.")

print(f"\nStatus: {result.status}")
for i, step in enumerate(result.history, 1):
    mark = "OK" if step.success else "FAIL"
    print(f"{mark} Step {i}: {step.action}({step.arguments}) - {step.explanation}")

browser_close()