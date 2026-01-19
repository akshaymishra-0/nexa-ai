"""
Speech Recognition Service for AVA.
Handles converting speech to text using various backends.
"""
import speech_recognition as sr
from typing import Optional, Tuple
from utils.helpers import log_message


class SpeechRecognitionService:
    """Service for converting speech to text."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise on initialization
        self._calibrate_microphone()
    
    def _calibrate_microphone(self) -> None:
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            log_message(f"Error calibrating microphone: {e}", "error")
    
    def listen(self, timeout: int = 15, phrase_time_limit: int = 60) -> Tuple[bool, Optional[str]]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Maximum seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase (longer for complete sentences)
            
        Returns:
            Tuple of (success, text or error message)
        """
        try:
            with self.microphone as source:
                log_message("Listening...", "info")
                # Dynamically adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
            # Use Google's free speech recognition
            text = self.recognizer.recognize_google(audio)
            return True, text.lower()
            
        except sr.WaitTimeoutError:
            return False, "Listening timed out. No speech detected."
        except sr.UnknownValueError:
            return False, "Could not understand audio."
        except sr.RequestError as e:
            return False, f"Speech recognition service error: {e}"
        except Exception as e:
            return False, f"Error during speech recognition: {e}"
    
    def listen_for_wake_word(self, wake_word: str, timeout: int = None) -> bool:
        """
        Listen continuously for the wake word.
        
        Args:
            wake_word: The word that activates the assistant
            timeout: Optional timeout in seconds
            
        Returns:
            True if wake word detected, False otherwise
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
                
            text = self.recognizer.recognize_google(audio).lower()
            return wake_word.lower() in text
            
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return False
        except Exception:
            return False
