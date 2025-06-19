import sys
import time
from typing import Optional, Tuple
import pyttsx3
import numpy as np
from dataclasses import dataclass

try:
    import pyaudio
    import speech_recognition as sr
    ONLINE_MODE_AVAILABLE = True
except ImportError:
    ONLINE_MODE_AVAILABLE = False

try:
    import whisper
    OFFLINE_MODE_AVAILABLE = True
except ImportError:
    OFFLINE_MODE_AVAILABLE = False

@dataclass
class AudioDevice:
    index: int
    name: str
    is_input: bool
    is_output: bool

class VoiceEngine:
    def __init__(self, use_offline: bool = False, energy_threshold: int = 3000):
        """
        Initialize voice engine with fallback modes
        
        Args:
            use_offline: Force offline Whisper mode
            energy_threshold: Audio detection sensitivity (3000-4000 recommended)
        """
        self.energy_threshold = energy_threshold
        self._init_modes(use_offline)
        self._init_audio_devices()
        self._init_tts()

    def _init_modes(self, use_offline):
        """Initialize recognition modes with proper fallbacks"""
        if use_offline and not OFFLINE_MODE_AVAILABLE:
            raise RuntimeError("Offline mode requested but Whisper not installed")
        
        self.use_offline = use_offline
        
        if not use_offline and not ONLINE_MODE_AVAILABLE:
            print("Warning: Online mode unavailable, falling back to offline")
            self.use_offline = True

        if self.use_offline and OFFLINE_MODE_AVAILABLE:
            print("Initializing offline voice recognition...")
            self.model = whisper.load_model("base")
        elif not self.use_offline:
            print("Initializing online voice recognition...")
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = False

    def _init_audio_devices(self):
        """Detect available audio devices"""
        self.audio_devices = []
        self.input_device_index = 0
        self.output_device_index = 0
        
        if ONLINE_MODE_AVAILABLE:
            try:
                p = pyaudio.PyAudio()
                for i in range(p.get_device_count()):
                    dev = p.get_device_info_by_index(i)
                    self.audio_devices.append(
                        AudioDevice(
                            index=i,
                            name=dev['name'],
                            is_input=dev['maxInputChannels'] > 0,
                            is_output=dev['maxOutputChannels'] > 0
                        )
                    )
                p.terminate()
                
                # Auto-select first input device
                for dev in self.audio_devices:
                    if dev.is_input:
                        self.input_device_index = dev.index
                        break
                        
            except Exception as e:
                print(f"Audio device detection failed: {str(e)}")

    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Try to find a natural-sounding voice
            preferred_voices = ['david', 'zira', 'english']
            for voice in voices:
                if any(v in voice.name.lower() for v in preferred_voices):
                    self.engine.setProperty('voice', voice.id)
                    break
                    
            self.engine.setProperty('rate', 180)
        except Exception as e:
            print(f"TTS initialization failed: {str(e)}")
            self.engine = None

    def list_audio_devices(self) -> list[AudioDevice]:
        """List all available audio devices"""
        return self.audio_devices

    def set_input_device(self, device_index: int):
        """Set specific input device by index"""
        if any(dev.index == device_index and dev.is_input for dev in self.audio_devices):
            self.input_device_index = device_index
        else:
            raise ValueError("Invalid input device index")

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Tuple[bool, str]:
        """
        Listen for voice input with robust error handling
        
        Returns:
            Tuple (success, text) where success indicates if audio was captured
        """
        try:
            if self.use_offline:
                return self._listen_offline(timeout)
            return self._listen_online(timeout, phrase_time_limit)
        except Exception as e:
            print(f"Listening error: {str(e)}")
            return False, ""

    def _listen_online(self, timeout: int, phrase_time_limit: int) -> Tuple[bool, str]:
        """Online recognition using Google Speech Recognition"""
        if not ONLINE_MODE_AVAILABLE:
            return False, "Online mode not available"

        with sr.Microphone(device_index=self.input_device_index) as source:
            try:
                print("\nListening... (Speak now)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                text = self.recognizer.recognize_google(audio)
                return True, text.lower()
                
            except sr.WaitTimeoutError:
                return False, ""
            except sr.UnknownValueError:
                return False, "Could not understand audio"
            except sr.RequestError as e:
                return False, f"API unavailable: {str(e)}"

    def _listen_offline(self, timeout: int) -> Tuple[bool, str]:
        """Offline recognition using Whisper"""
        if not OFFLINE_MODE_AVAILABLE:
            return False, "Offline mode not available"

        try:
            import sounddevice as sd
            print("\nListening offline... (Speak now)")
            
            fs = 16000  # Sample rate
            recording = sd.rec(int(timeout * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished
            
            audio = whisper.pad_or_trim(recording)
            result = self.model.transcribe(audio)
            return True, result["text"].lower()
            
        except Exception as e:
            return False, f"Offline recognition failed: {str(e)}"

    def speak(self, text: str, wait: bool = True) -> bool:
        """Convert text to speech with error handling"""
        if not self.engine:
            print("TTS engine not available")
            return False
            
        try:
            print(f"Speaking: {text}")
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Speech synthesis failed: {str(e)}")
            return False

    def play_activation_sound(self):
        """Play a brief activation sound"""
        self.speak("Activated", wait=False)

if __name__ == "__main__":
    # Test the voice interface
    print("Testing Voice Engine...")
    
    engine = VoiceEngine(use_offline=not ONLINE_MODE_AVAILABLE)
    print("\nAvailable audio devices:")
    for dev in engine.list_audio_devices():
        print(f"{dev.index}: {dev.name} (In: {dev.is_input}, Out: {dev.is_output})")
    
    print("\nSpeak after the beep...")
    engine.play_activation_sound()
    
    success, text = engine.listen(timeout=5)
    if success:
        print(f"\nYou said: {text}")
        engine.speak(f"I heard: {text}")
    else:
        print("\nNo speech detected or recognition failed")