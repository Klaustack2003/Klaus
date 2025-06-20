import time
import numpy as np
import pyttsx3
import threading
from .utils import is_android
from typing import Tuple, Optional

try:
    import sounddevice as sd
    import whisper
    OFFLINE_ENABLED = True
except ImportError:
    OFFLINE_ENABLED = False

class VoiceEngine:
    def __init__(self, use_offline=True, energy_threshold=4000):
        self.use_offline = use_offline
        self.energy_threshold = energy_threshold
        self._init_tts()
        self._init_recognition()
        
    def _init_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            voices = self.engine.getProperty('voices')
            
            # Voice selection
            for voice in voices:
                if 'english' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except:
            self.engine = None
    
    def _init_recognition(self):
        if self.use_offline and OFFLINE_ENABLED:
            try:
                import whisper
                self.model = whisper.load_model("tiny")
            except:
                self.use_offline = False
    
    def listen(self, timeout=5) -> Tuple[bool, str]:
        try:
            if self.use_offline:
                return self._listen_offline(timeout)
            return self._listen_online(timeout)
        except Exception as e:
            print(f"Listen error: {str(e)}")
            return False, ""
    
    def _listen_online(self, timeout) -> Tuple[bool, str]:
        """Fallback to offline if online not available"""
        if not hasattr(self, 'recognizer'):
            return self._listen_offline(timeout)
            
        try:
            import speech_recognition as sr
            with sr.Microphone() as source:
                audio = sr.recognizer.listen(source, timeout=timeout)
                text = sr.recognizer.recognize_google(audio)
                return True, text.lower()
        except:
            return self._listen_offline(timeout)
    
    def _listen_offline(self, timeout) -> Tuple[bool, str]:
        try:
            fs = 16000
            recording = sd.rec(int(timeout * fs), 
                              samplerate=fs, 
                              channels=1, 
                              blocking=True)
            
            audio = np.array(recording, dtype=np.float32).flatten()
            result = self.model.transcribe(audio)
            return True, result["text"].lower()
        except Exception as e:
            return False, f"Offline error: {str(e)}"
    
    def speak(self, text: str):
        if not self.engine:
            return
            
        def speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
                
        threading.Thread(target=speak_thread, daemon=True).start()