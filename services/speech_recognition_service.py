"""
Speech Recognition Service for NEXA.
Uses Faster-Whisper for fast, accurate offline speech recognition.
Supports continuous listening with wake word activation.
"""
import os
import tempfile
import threading
import time
import speech_recognition as sr
from faster_whisper import WhisperModel
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from utils.helpers import log_message
from config.settings import settings


class SpeechRecognitionService:
    """Service for converting speech to text using Faster-Whisper."""
    
    # Whisper model sizes: tiny, base, small, medium, large-v3
    # tiny = fastest, base = good balance, small/medium = more accurate
    MODEL_SIZE = "base"
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.whisper_model = None
        
        # Continuous listening state
        self.is_listening = False
        self.is_active = False  # True when wake word detected, False when sleeping
        self.last_activity_time = 0
        self.stop_listening_event = threading.Event()
        self.audio_queue = []
        self.audio_lock = threading.Lock()
        
        self._load_whisper_model()
        self._calibrate_microphone()
        self._configure_recognizer()
    
    def _configure_recognizer(self):
        """Configure recognizer for better phrase detection."""
        # Wait longer for user to finish speaking (pause threshold)
        self.recognizer.pause_threshold = 2.0  # seconds of silence before phrase is considered complete
        # Minimum length of silence to consider as end of phrase
        self.recognizer.non_speaking_duration = 1.0
        # Energy threshold for detecting speech (auto-adjusted)
        self.recognizer.dynamic_energy_threshold = True
    
    def _load_whisper_model(self):
        """Load Faster-Whisper model for offline recognition."""
        try:
            log_message(f"Loading Whisper model ({self.MODEL_SIZE})...", "info")
            self.whisper_model = WhisperModel(
                self.MODEL_SIZE,
                device="cpu",
                compute_type="int8"  # Faster on CPU
            )
            log_message("Whisper model loaded!", "success")
        except Exception as e:
            log_message(f"Error loading Whisper model: {e}", "error")
            self.whisper_model = None
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            log_message(f"Error calibrating microphone: {e}", "error")
    
    def _transcribe_with_whisper(self, audio_data) -> tuple:
        """Transcribe audio using Faster-Whisper."""
        if not self.whisper_model:
            # Fallback to Google if Whisper not loaded
            try:
                text = self.recognizer.recognize_google(audio_data)
                return True, text.lower()
            except:
                return False, "Speech recognition unavailable"
        
        temp_path = None
        try:
            # Save audio to temp file
            temp_path = os.path.join(tempfile.gettempdir(), f"nexa_audio_{os.getpid()}.wav")
            with open(temp_path, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            # Transcribe with Faster-Whisper (auto-detect language)
            segments, _ = self.whisper_model.transcribe(
                temp_path,
                language="en",
                beam_size=5,
                vad_filter=True
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()
            
            if text:
                return True, text.lower()
            else:
                return False, "No speech detected"
                
        except Exception as e:
            log_message(f"Whisper error: {e}", "error")
            # Fallback to Google
            try:
                text = self.recognizer.recognize_google(audio_data)
                return True, text.lower()
            except:
                return False, f"Transcription error: {e}"
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def listen(self, timeout: int = 10, phrase_time_limit: int = 30) -> tuple:
        """
        Listen for speech and convert to text using Whisper.
        
        Args:
            timeout: Maximum seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase
            
        Returns:
            Tuple of (success, text or error message)
        """
        try:
            with self.microphone as source:
                log_message("Listening...", "info")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            return self._transcribe_with_whisper(audio)
            
        except sr.WaitTimeoutError:
            return False, "Listening timed out."
        except Exception as e:
            return False, f"Error: {e}"
    
    def listen_for_wake_word(self, wake_word: str, timeout: int = None) -> bool:
        """Listen for the wake word."""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
            
            success, text = self._transcribe_with_whisper(audio)
            if success:
                return wake_word.lower() in text.lower()
            return False
            
        except:
            return False
    
    def continuous_listen(self, callback, wake_word: str = None, stop_word: str = None):
        """
        Continuously listen for audio and process with callbacks.
        
        Args:
            callback: Function to call with (is_wake_word, is_stop_word, text)
            wake_word: Word to activate the assistant
            stop_word: Word to deactivate the assistant
        """
        self.is_listening = True
        self.stop_listening_event.clear()
        
        wake_word = wake_word or settings.WAKE_WORD
        stop_word = stop_word or settings.STOP_WORD
        
        log_message(f"Continuous listening started. Wake word: '{wake_word}', Stop word: '{stop_word}'", "info")
        
        while self.is_listening and not self.stop_listening_event.is_set():
            try:
                with self.microphone as source:
                    # Quick ambient noise adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    
                    try:
                        # Listen with short timeout for responsiveness
                        audio = self.recognizer.listen(
                            source,
                            timeout=settings.WAKE_TIMEOUT if not self.is_active else 10,
                            phrase_time_limit=15 if self.is_active else 5
                        )
                    except sr.WaitTimeoutError:
                        # Check if we should go back to sleep (inactive timeout)
                        if self.is_active and settings.ACTIVE_TIMEOUT:
                            if time.time() - self.last_activity_time > settings.ACTIVE_TIMEOUT:
                                self.is_active = False
                                callback("__SLEEP__", None)
                        continue
                
                # Transcribe the audio
                success, text = self._transcribe_with_whisper(audio)
                
                if not success or not text:
                    continue
                
                text = text.strip().lower()
                
                # Check for wake word
                contains_wake_word = wake_word.lower() in text
                
                # Check for stop word
                contains_stop_word = stop_word.lower() in text
                
                # Check for goodbye words
                is_goodbye = any(word in text for word in settings.GOODBYE_WORDS)
                
                if contains_wake_word:
                    self.is_active = True
                    self.last_activity_time = time.time()
                    # Remove wake word from text for processing
                    clean_text = text.replace(wake_word.lower(), '').strip()
                    callback("__WAKE__", clean_text if clean_text else None)
                
                elif contains_stop_word and self.is_active:
                    self.is_active = False
                    callback("__STOP__", text)
                
                elif is_goodbye and self.is_active:
                    callback("__GOODBYE__", text)
                
                elif self.is_active:
                    # Normal command/conversation when active
                    self.last_activity_time = time.time()
                    callback("__INPUT__", text)
                
                # If not active and no wake word, just continue listening silently
                    
            except Exception as e:
                log_message(f"Continuous listen error: {e}", "error")
                time.sleep(0.5)  # Brief pause before retrying
        
        log_message("Continuous listening stopped", "info")
    
    def stop_continuous_listen(self):
        """Stop continuous listening."""
        self.is_listening = False
        self.stop_listening_event.set()
    
    def activate(self):
        """Manually activate the assistant (as if wake word was detected)."""
        self.is_active = True
        self.last_activity_time = time.time()
    
    def deactivate(self):
        """Manually deactivate the assistant (as if stop word was detected)."""
        self.is_active = False
