import numpy as np
import re

class AudioUtils:
    @staticmethod
    def clean_transcript(text: str) -> str:
        text = re.sub(r'\[BLANK_AUDIO\]', '', text)
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        text = re.sub(r'[.!?]+$', '', text)
        return ' '.join(text.split()).strip()

    @staticmethod
    def is_meaningful_speech(text: str) -> bool:
        cleaned = AudioUtils.clean_transcript(text)
        return bool(cleaned and not cleaned.isspace())

    @staticmethod
    def detect_silence(audio_data: np.ndarray, threshold: float) -> bool:
        amplitude = np.abs(audio_data).mean()
        return amplitude < threshold