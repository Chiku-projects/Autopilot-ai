from app.voice.stt import get_speech_provider
from app.agent.loop import AgentLoop
from app.tools.browser import browser_close

provider = get_speech_provider()

input("Press Enter, then speak your command (you'll have 5 seconds)...")
text = provider.record_and_transcribe(duration_seconds=5.0)
print(f"\nTranscribed: \"{text}\"")

confirm = input("Run this as a task? (y/n): ")
if confirm.lower() == "y":
    loop = AgentLoop()
    result = loop.run(text)
    print(f"\nStatus: {result.status}")
    for i, step in enumerate(result.history, 1):
        mark = "OK" if step.success else "FAIL"
        print(f"{mark} Step {i}: {step.action}({step.arguments}) - {step.explanation}")
    browser_close()