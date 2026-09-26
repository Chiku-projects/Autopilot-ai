import logging
import tempfile
import threading
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000


class SpeechProvider(ABC):
    @abstractmethod
    def record_and_transcribe(self, duration_seconds: float = 5.0) -> str:
        ...


class GroqSpeechProvider(SpeechProvider):
    def __init__(self):
        self._client = Groq(api_key=settings.groq_api_key)

    def record_and_transcribe(self, duration_seconds: float | None = None) -> str:
        """
        If duration_seconds is given, records for a fixed window.
        If None, records until Enter is pressed (recommended for real use —
        avoids cutting speech off or wasting time on trailing silence).
        """
        if duration_seconds is not None:
            audio = self._record_fixed(duration_seconds)
        else:
            audio = self._record_until_enter()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            write_wav(tmp.name, SAMPLE_RATE, audio)
            tmp_path = Path(tmp.name)

        try:
            with open(tmp_path, "rb") as f:
                transcript = self._client.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3-turbo",
                    response_format="text",
                )
            return str(transcript).strip()
        finally:
            tmp_path.unlink(missing_ok=True)

    def _record_fixed(self, duration_seconds: float) -> np.ndarray:
        logger.info("Recording for %.1f seconds...", duration_seconds)
        audio = sd.rec(
            int(duration_seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        return audio

    def _record_until_enter(self) -> np.ndarray:
        frames = []

        def callback(indata, frame_count, time_info, status):
            if status:
                logger.warning("Mic input status: %s", status)
            frames.append(indata.copy())

        stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback
        )
        logger.info("Recording... press Enter when done.")
        print("Recording... press Enter when done.")
        stream.start()
        input()
        stream.stop()
        stream.close()

        if frames:
            return np.concatenate(frames, axis=0)
        return np.zeros((0, 1), dtype="int16")


def get_speech_provider() -> SpeechProvider:
    return GroqSpeechProvider()