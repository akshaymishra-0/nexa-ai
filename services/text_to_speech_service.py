"""
Text to Speech Service for AVA.
Uses Edge TTS for natural, realistic voice output with emotional expression.
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import edge_tts
import asyncio
import tempfile
import time
import re
import keyboard
from pygame import mixer
from utils.helpers import log_message


class TextToSpeechService:
    """Service for converting text to speech using Edge TTS with emotions."""
    
    # Voices that support speaking styles (emotions)
    VOICES = {
        # Expressive voices with style support
        "jenny": "en-US-JennyNeural",      # Supports many styles
        "aria": "en-US-AriaNeural",         # Supports many styles
        "sara": "en-US-SaraNeural",         # Cheerful, friendly
        "sonia": "en-GB-SoniaNeural",       # UK voice
        "natasha": "en-AU-NatashaNeural",   # Australian
        "neerja": "en-IN-NeerjaNeural",     # Indian English
        "aarav": "en-IN-PrabhatNeural",     # Indian Male
        "swara": "hi-IN-SwaraNeural",       # Hindi Female
        "madhur": "hi-IN-MadhurNeural",     # Hindi Male
    }
    
    # Emotion to voice settings mapping
    EMOTION_STYLES = {
        "happy": {"pitch": "+5Hz", "rate": "+10%"},
        "excited": {"pitch": "+10Hz", "rate": "+15%"},
        "sad": {"pitch": "-5Hz", "rate": "-10%"},
        "caring": {"pitch": "+2Hz", "rate": "-5%"},
        "loving": {"pitch": "+3Hz", "rate": "-5%"},
        "flirty": {"pitch": "+8Hz", "rate": "+5%"},
        "playful": {"pitch": "+5Hz", "rate": "+8%"},
        "worried": {"pitch": "-3Hz", "rate": "-5%"},
        "angry": {"pitch": "+5Hz", "rate": "+5%"},
        "neutral": {"pitch": "+0Hz", "rate": "+0%"},
    }
    
    def __init__(self):
        self.voice = self.VOICES.get("neerja", "en-IN-NeerjaNeural")
        self.base_rate = "+5%"
        self.volume = "+0%"
        self.is_speaking = False
        self.was_interrupted = False
        self.last_response = ""
        self.current_emotion = "excited"
        
        try:
            mixer.init()
        except Exception as e:
            log_message(f"Error initializing audio: {e}", "error")
    
    def _detect_emotion(self, text: str) -> tuple:
        """Detect emotion marker from text and return (emotion, clean_text)."""
        emotion_pattern = r'^\[(\w+)\]\s*'
        match = re.match(emotion_pattern, text)
        
        if match:
            emotion = match.group(1).lower()
            clean_text = re.sub(emotion_pattern, '', text)
            if emotion in self.EMOTION_STYLES:
                return emotion, clean_text
        
        # Auto-detect emotion from content if no marker
        text_lower = text.lower()
        if any(word in text_lower for word in ["haha", "hehe", "lol", "funny", "excited"]):
            return "happy", text
        elif any(word in text_lower for word in ["miss you", "love you", "jaan", "sweetheart"]):
            return "loving", text
        elif any(word in text_lower for word in ["aww", "baby", "take care", "worried"]):
            return "caring", text
        elif any(word in text_lower for word in ["proud", "amazing", "wow", "yay"]):
            return "excited", text
        
        return "neutral", text
    
    def _apply_emotion(self, text: str, emotion: str) -> tuple:
        """Apply emotion settings and return (modified_text, rate, pitch)."""
        style = self.EMOTION_STYLES.get(emotion, self.EMOTION_STYLES["neutral"])
        
        # Add natural speech elements based on emotion
        if emotion == "happy" or emotion == "playful":
            # Add slight pauses for natural rhythm
            text = text.replace("!", "! ")
        elif emotion == "caring" or emotion == "loving":
            # Slower, more gentle speech
            text = text.replace(",", ", ")
        
        rate = style["rate"]
        pitch = style["pitch"]
        
        self.current_emotion = emotion
        return text, rate, pitch
    
    def _run_async(self, coro):
        """Run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    async def _generate_speech(self, text: str, output_file: str, rate: str, pitch: str) -> bool:
        """Generate speech audio file from text with emotion."""
        try:
            communicate = edge_tts.Communicate(
                text, 
                self.voice, 
                rate=rate, 
                volume=self.volume,
                pitch=pitch
            )
            await communicate.save(output_file)
            return True
        except Exception as e:
            log_message(f"Error generating speech: {e}", "error")
            return False
    
    def stop(self):
        """Stop current speech playback."""
        if self.is_speaking:
            try:
                mixer.music.stop()
                self.was_interrupted = True
                self.is_speaking = False
            except:
                pass
    
    def speak(self, text: str, interruptible: bool = True) -> bool:
        """Convert text to speech with emotion and play it."""
        if not text:
            return False
        
        self.last_response = text
        self.was_interrupted = False
        temp_file = None
        
        # Detect and apply emotion
        emotion, clean_text = self._detect_emotion(text)
        processed_text, rate, pitch = self._apply_emotion(clean_text, emotion)
        
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()
            
            success = self._run_async(self._generate_speech(processed_text, temp_path, rate, pitch))
            
            if not success:
                return False
            
            mixer.music.load(temp_path)
            mixer.music.play()
            self.is_speaking = True
            
            while mixer.music.get_busy():
                if interruptible:
                    try:
                        if keyboard.is_pressed('space'):
                            self.stop()
                            break
                    except:
                        pass
                time.sleep(0.1)
            
            self.is_speaking = False
            
            try:
                mixer.music.unload()
                os.unlink(temp_path)
            except:
                pass
            
            return not self.was_interrupted
            
        except Exception as e:
            log_message(f"Error during text-to-speech: {e}", "error")
            self.is_speaking = False
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            return False
    
    def continue_speaking(self) -> bool:
        """Continue speaking the last response."""
        if self.last_response:
            return self.speak(self.last_response)
        return False
    
    def set_voice(self, voice_name: str) -> bool:
        """Change the voice being used."""
        if voice_name.lower() in self.VOICES:
            self.voice = self.VOICES[voice_name.lower()]
            return True
        return False
    
    def get_available_voices(self) -> dict:
        """Get list of available voice names."""
        return self.VOICES.copy()
