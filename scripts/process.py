from transformers import pipeline
from collections import deque
from vosk import Model, KaldiRecognizer

from scripts.config import Config
from scripts.utils import AudioUtils

import numpy as np
import time
import torch
import ast

class AudioProcessor:
    def __init__(self):
        self.config = Config()
        self.utils = AudioUtils()
        self.complete_text = ""
        self.current_partial = ""
        self.last_speech_time = time.time()
        self.silence_detected = False
        self.partial_buffer = deque(maxlen=self.config.MAX_PARTIAL_SECONDS)
        
        if self.config.MODEL_TYPE == "huggingface":
            self._init_huggingface()
        else:
            self._init_vosk()

    def _init_huggingface(self):
        self.model = pipeline(
            "automatic-speech-recognition",
            model=self.config.HUGGINGFACE_MODEL,
            device="cuda" if torch.cuda.is_available() else "cpu",
            generate_kwargs={
                "language": "en",
                "task": "transcribe",
                "no_repeat_ngram_size": 5,
                "temperature": 0.0,
                "do_sample": False,
                "max_new_tokens": 20,
                "length_penalty": 5.0,
                "suppress_tokens": [1391, 1767, 1768],
                "num_beams": 1,
                "early_stopping": True,
                "return_timestamps": False
            }
        )

    def _init_vosk(self):
        self.model = Model(self.config.VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, self.config.RATE)

    def get_current_text(self):
        text = self.complete_text
        if self.current_partial:
            text += (" " if text else "") + self.current_partial
        return text.strip()

    def process_audio_chunk(self, audio_data):
        try:
            # Check for silence
            if self.utils.detect_silence(audio_data, self.config.SILENCE_THRESHOLD):
                if not self.silence_detected and time.time() - self.last_speech_time >= self.config.SILENCE_DURATION:
                    self.silence_detected = True
                    if self.current_partial:
                        self.complete_text += (" " if self.complete_text else "") + self.current_partial + "."
                        self.current_partial = ""
                    return self.get_current_text()
            else:
                self.last_speech_time = time.time()
                self.silence_detected = False

            if self.config.MODEL_TYPE == "huggingface":
                return self._process_huggingface(audio_data)
            else:
                return self._process_vosk(audio_data)

        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return self.get_current_text()

    def _process_huggingface(self, audio_data):
        self.partial_buffer.append(audio_data)
        
        if len(self.partial_buffer) > 0:
            partial_audio = np.concatenate(list(self.partial_buffer))
            result = self.model(partial_audio)
            text = result["text"].strip()
            
            if self.utils.is_meaningful_speech(text):
                cleaned_text = self.utils.clean_transcript(text)
                
                if len(self.partial_buffer) >= self.config.MAX_PARTIAL_SECONDS:
                    if cleaned_text:
                        self.complete_text += (" " if self.complete_text else "") + cleaned_text
                        self.current_partial = ""
                    self.partial_buffer.clear()
                else:
                    self.current_partial = cleaned_text
                
        return self.get_current_text()

    def _process_vosk(self, audio_data):
        audio_data_int16 = (audio_data * 32768).astype(np.int16).tobytes()
        
        if not self.recognizer.AcceptWaveform(audio_data_int16):
            partial = self.recognizer.PartialResult()
            try:
                partial_dict = ast.literal_eval(partial)
                if 'partial' in partial_dict:
                    partial_text = self.utils.clean_transcript(partial_dict['partial'])
                    if self.utils.is_meaningful_speech(partial_text):
                        self.current_partial = partial_text
            except (ValueError, SyntaxError):
                pass
        else:
            result = self.recognizer.Result()
            try:
                result_dict = ast.literal_eval(result)
                if 'text' in result_dict:
                    text = self.utils.clean_transcript(result_dict['text'])
                    if self.utils.is_meaningful_speech(text):
                        self.complete_text += (" " if self.complete_text else "") + text
                        self.current_partial = ""
            except (ValueError, SyntaxError):
                pass

        return self.get_current_text()