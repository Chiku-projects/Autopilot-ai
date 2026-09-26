from app.voice.stt import get_speech_provider
provider = get_speech_provider()
text = provider.record_and_transcribe()  # press Enter when done speaking
print("Transcribed:", text)