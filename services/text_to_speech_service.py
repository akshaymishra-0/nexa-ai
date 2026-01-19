"""
Text to Speech Service for AVA.
Uses Edge TTS for natural, realistic voice output.
"""
import edge_tts
import asyncio
import tempfile
import os
import threading
import time
import keyboard
from pygame import mixer
from typing import Optional
from utils.helpers import log_message
from config.settings import settings


class TextToSpeechService:
    """Service for converting text to speech using Edge TTS."""
    
    # Available realistic voices
    VOICES = {
        # US Voices
        "jenny": "en-US-JennyNeural",       # US Female (friendly)
        "aria": "en-US-AriaNeural",          # US Female (professional)
        "sara": "en-US-SaraNeural",          # US Female (cheerful)
        # UK Voices
        "sonia": "en-GB-SoniaNeural",        # UK Female
        # Australian Voices
        "natasha": "en-AU-NatashaNeural",    # Australian Female
        # Indian English Voices
        "neerja": "en-IN-NeerjaNeural",      # Indian Female (professional)
        "aarav": "en-IN-PrabhatNeural",       # Indian Male
        # Hindi Voices
        "swara": "hi-IN-SwaraNeural",        # Hindi Female
        "madhur": "hi-IN-MadhurNeural",      # Hindi Male
        # Bengali Voices
        "tanishaa": "bn-IN-TanishaaNeural",  # Bengali Female
        "bashkar": "bn-IN-BashkarNeural",    # Bengali Male
    }
    
    def __init__(self):
        self.voice = self.VOICES.get("neerja", "en-IN-NeerjaNeural")
        self.rate = "+20%"  # Speech rate adjustment
        self.volume = "+0%"  # Volume adjustment
        self.is_speaking = False
        self.was_interrupted = False
        self.last_response = ""
        self.interrupt_position = 0
        
        # Initialize pygame mixer for audio playback
        try:
            mixer.init()
        except Exception as e:
            log_message(f"Error initializing audio: {e}", "error")
    
    def _run_async(self, coro):
        """Run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    async def _generate_speech(self, text: str, output_file: str) -> bool:
        """Generate speech audio file from text."""
        try:
            communicate = edge_tts.Communicate(
                text, 
                self.voice,
                rate=self.rate,
                volume=self.volume
            )
            await communicate.save(output_file)
            return True
        except Exception as e:
            log_message(f"Error generating speech: {e}", "error")
            return False
    
    def stop(self) -> None:
        """Stop current speech playback."""
        if self.is_speaking:
            try:
                mixer.music.stop()
                self.was_interrupted = True
                self.is_speaking = False
            except:
                pass
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return mixer.music.get_busy()
    
    def speak(self, text: str, interruptible: bool = True) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to speak
            interruptible: Whether the speech can be interrupted by keyboard
            
        Returns:
            True if completed successfully, False if interrupted or error
        """
        if not text:
            return False
        
        self.last_response = text
        self.was_interrupted = False
        temp_file = None
        
        try:
            # Create temp file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate speech
            success = self._run_async(self._generate_speech(text, temp_path))
            
            if not success:
                return False
            
            # Play the audio
            mixer.music.load(temp_path)
            mixer.music.play()
            self.is_speaking = True
            
            # Wait for playback to finish, checking for interrupts
            while mixer.music.get_busy():
                if interruptible:
                    # Check for spacebar press to interrupt
                    try:
                        if keyboard.is_pressed('space'):
                            self.stop()
                            break
                    except:
                        pass
                time.sleep(0.1)
            
            self.is_speaking = False
            
            # Cleanup
            try:
                mixer.music.unload()
                os.unlink(temp_path)
            except:
                pass
            
            return not self.was_interrupted
            
        except Exception as e:
            log_message(f"Error during text-to-speech: {e}", "error")
            self.is_speaking = False
            # Cleanup on error
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
        """
        Change the voice being used.
        
        Args:
            voice_name: One of 'jenny', 'aria', 'sara', 'emma', 'natasha'
        """
        if voice_name.lower() in self.VOICES:
            self.voice = self.VOICES[voice_name.lower()]
            return True
        return False
    
    def set_rate(self, rate: int) -> bool:
        """
        Change the speech rate.
        
        Args:
            rate: Percentage adjustment (-50 to +50)
        """
        try:
            self.rate = f"{rate:+d}%"
            return True
        except Exception as e:
            log_message(f"Error setting rate: {e}", "error")
            return False
    
    def get_available_voices(self) -> dict:
        """Get list of available voice names."""
        return self.VOICES.copy()
