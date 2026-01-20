"""
Main Assistant class for NEXA.
Orchestrates all services and handles the main interaction loop.
"""
import random
from config.settings import settings
from services.speech_recognition_service import SpeechRecognitionService
from services.text_to_speech_service import TextToSpeechService
from services.ai_service import AIService
from commands.base_command import CommandRegistry
from commands.system_commands import (
    TimeCommand, DateCommand, ExitCommand, 
    OpenWebsiteCommand, HelpCommand, ContinueCommand, StopCommand
)
from commands.local_commands import (
    OpenAppCommand, CloseAppCommand, BrowserSearchCommand,
    PlayVideoCommand, VolumeControlCommand, SystemControlCommand,
    ScreenshotCommand
)
from .conversation import ConversationManager
from utils.helpers import log_message, get_greeting, print_colored, clean_text_for_speech, remove_emotion_markers, romanize_text


class Assistant:
    """Main NEXA Assistant class."""
    
    # Random questions NEXA asks when user is silent
    RANDOM_QUESTIONS = [
        "What's on your mind today?",
        "How's your day going so far?",
        "Did anything interesting happen today?",
        "What are you working on?",
        "Have you eaten anything yet?",
        "Want to hear a fun fact?",
        "Should I play some music for you?",
        "Is there anything I can help you with?",
        "What are your plans for later?",
        "Did you sleep well last night?",
        "Want me to tell you a joke?",
        "How are you feeling right now?",
        "Anything exciting happening this week?",
        "Should I remind you about something?",
        "Want to chat about something random?",
    ]
    
    def __init__(self):
        self.name = settings.ASSISTANT_NAME
        self.wake_word = settings.WAKE_WORD
        self.stop_word = settings.STOP_WORD
        self.is_running = False
        self.silent_count = 0  # Track consecutive silent periods
        self.speech_recognition = SpeechRecognitionService()
        self.tts = TextToSpeechService()
        self.ai = AIService()
        self.conversation = ConversationManager()
        self.commands = CommandRegistry()
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register built-in commands."""
        self.commands.register(TimeCommand())
        self.commands.register(DateCommand())
        self.commands.register(ExitCommand())
        self.commands.register(OpenWebsiteCommand())
        self.commands.register(HelpCommand(self.commands))
        self.commands.register(ContinueCommand(self.tts))
        self.commands.register(StopCommand(self.tts))
        self.commands.register(OpenAppCommand())
        self.commands.register(CloseAppCommand())
        self.commands.register(BrowserSearchCommand())
        self.commands.register(PlayVideoCommand())
        self.commands.register(VolumeControlCommand())
        self.commands.register(SystemControlCommand())
        self.commands.register(ScreenshotCommand())
    
    def greet(self):
        """Greet the user."""
        greeting = get_greeting()
        message = f"{greeting}! I'm {self.name}, your personal AI assistant. How can I help you today?"
        print_colored(f"\n{self.name}: {message}", "cyan")
        self.tts.speak(message)
    
    def process_input(self, user_input: str):
        """Process user input and generate response."""
        if not user_input:
            return "I didn't catch that. Could you please repeat?"
        
        command_response = self.commands.execute(user_input)
        
        if command_response:
            if command_response == "__EXIT__":
                return None
            if command_response == "__CONTINUE__":
                return "__CONTINUE__"
            if command_response == "__STOP__":
                self.tts.stop()
                return "Okay, I'll be quiet."
            return command_response
        
        ai_response = self.ai.get_response(user_input)
        self.conversation.add_exchange(user_input, ai_response or "")
        return ai_response
    
    def respond(self, response: str):
        """Output response via speech and text."""
        display_response = remove_emotion_markers(response)
        print_colored(f"\n{self.name}: {display_response}", "cyan")
        clean_response = clean_text_for_speech(response)
        self.tts.speak(clean_response)
    
    def _ask_random_question(self):
        """Ask a random question to initiate conversation."""
        question = random.choice(self.RANDOM_QUESTIONS)
        print_colored(f"\n{self.name}: {question}", "cyan")
        self.tts.speak(question)
        self.silent_count = 0
    
    def _handle_voice_callback(self, event_type: str, text: str):
        """
        Handle callbacks from continuous listening.
        
        Args:
            event_type: Type of event (__WAKE__, __STOP__, __GOODBYE__, __INPUT__, __SLEEP__)
            text: The transcribed text (may be None for some events)
        """
        try:
            if event_type == "__WAKE__":
                # Wake word detected - activate and respond
                self.silent_count = 0
                print_colored(f"\n[{self.name} activated!]", "green")
                
                if text:
                    # Wake word + command in same phrase
                    print_colored(f"\nYou: {text}", "green")
                    response = self.process_input(text)
                    if response and response not in ["__CONTINUE__", "__STOP__"]:
                        self.respond(response)
                else:
                    # Just wake word - acknowledge and wait for command
                    acknowledgments = ["Yes?", "I'm here!", "What's up?", "Hey!", "Listening!", "Yes, I'm here."]
                    ack = random.choice(acknowledgments)
                    print_colored(f"\n{self.name}: {ack}", "cyan")
                    self.tts.speak(ack)
            
            elif event_type == "__STOP__":
                # Stop word detected - go to sleep
                print_colored(f"\n[{self.name} going to sleep... Say '{self.wake_word}' to wake me up]", "yellow")
                sleep_responses = [
                    "Okay, I'll be quiet. Just say my name when you need me.",
                    "Going to sleep. Wake me up anytime!",
                    "Alright, taking a break. I'm here if you need me.",
                    "Okay, going quiet. Just call my name!",
                ]
                response = random.choice(sleep_responses)
                print_colored(f"\n{self.name}: {response}", "cyan")
                self.tts.speak(response)
            
            elif event_type == "__GOODBYE__":
                # Goodbye detected - shutdown
                self.shutdown()
            
            elif event_type == "__SLEEP__":
                # Auto-sleep due to inactivity timeout
                print_colored(f"\n[{self.name} going idle... Say '{self.wake_word}' to wake me up]", "yellow")
                self.tts.speak("I'll be here when you need me.")
            
            elif event_type == "__INPUT__":
                # Normal input when active
                self.silent_count = 0
                print_colored(f"\nYou: {text}", "green")
                response = self.process_input(text)
                
                if response is None:
                    self.shutdown()
                    return
                
                if response == "__CONTINUE__":
                    if self.tts.last_response:
                        self.respond(self.tts.last_response)
                    return
                
                if response == "__STOP__":
                    return
                
                if response:
                    self.respond(response)
                    
        except Exception as e:
            log_message(f"Error handling voice callback: {e}", "error")
    
    def run_voice_mode(self):
        """Run NEXA in continuous voice-activated mode (hands-free)."""
        self.is_running = True
        self.greet()
        
        # Activate immediately after greeting
        self.speech_recognition.activate()
        
        print_colored(f"\n{'='*60}", "yellow")
        print_colored(f"  HANDS-FREE MODE ACTIVE", "green")
        print_colored(f"  Wake word: '{self.wake_word}' | Stop word: '{self.stop_word}'", "yellow")
        print_colored(f"  Say '{self.wake_word}' to activate, '{self.stop_word}' to pause", "yellow")
        print_colored(f"  Say 'goodbye' to exit | Press Ctrl+C to force quit", "yellow")
        print_colored(f"{'='*60}\n", "yellow")
        
        try:
            # Start continuous listening with callback
            self.speech_recognition.continuous_listen(
                callback=self._handle_voice_callback,
                wake_word=self.wake_word,
                stop_word=self.stop_word
            )
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            log_message(f"Error in voice mode: {e}", "error")
            self.shutdown()
    
    def run_text_mode(self):
        """Run NEXA in text input mode (for testing without microphone)."""
        self.is_running = True
        self.greet()
        
        print_colored("\n[Text mode - Type your messages]", "yellow")
        print_colored("[Type 'exit' to quit | 'continue' to resume last response | Press SPACE during speech to stop]\n", "yellow")
        
        while self.is_running:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                response = self.process_input(user_input)
                
                if response is None:
                    self.shutdown()
                    break
                
                if response == "__CONTINUE__":
                    if self.tts.last_response:
                        print_colored(f"\n{self.name}: [Continuing...] {self.tts.last_response}", "cyan")
                        clean_response = clean_text_for_speech(self.tts.last_response)
                        self.tts.speak(clean_response)
                    else:
                        print_colored(f"\n{self.name}: There's nothing to continue.", "cyan")
                    continue
                
                self.respond(response)
                
            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                log_message(f"Error in text mode: {e}", "error")
    
    def shutdown(self):
        """Shutdown the assistant gracefully."""
        self.is_running = False
        self.speech_recognition.stop_continuous_listen()
        
        farewell = f"Goodbye! It was nice talking to you. {self.name} signing off."
        print_colored(f"\n{self.name}: {farewell}", "cyan")
        self.tts.speak(farewell)
        
        summary = self.conversation.get_summary()
        print_colored(f"\nSession duration: {summary['duration']}", "magenta")
        print_colored(f"Total exchanges: {summary['exchanges']}", "magenta")
