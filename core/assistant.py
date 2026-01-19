"""
Main Assistant class for AVA.
Orchestrates all services and handles the main interaction loop.
"""
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
from utils.helpers import log_message, get_greeting, print_colored, clean_text_for_speech


class Assistant:
    """Main AVA Assistant class."""
    
    def __init__(self):
        self.name = settings.ASSISTANT_NAME
        self.wake_word = settings.WAKE_WORD
        self.is_running = False
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
        print_colored(f"\n{self.name}: {response}", "cyan")
        clean_response = clean_text_for_speech(response)
        self.tts.speak(clean_response)
    
    def run_voice_mode(self):
        """Run AVA in voice-activated mode."""
        self.is_running = True
        self.greet()
        
        print_colored(f"\n[Say '{self.wake_word}' to activate, or speak your query directly]", "yellow")
        print_colored("[Say 'goodbye' to exit | Press SPACE to interrupt speech]\n", "yellow")
        
        while self.is_running:
            try:
                success, user_input = self.speech_recognition.listen(timeout=10)
                
                if success and user_input:
                    print_colored(f"\nYou: {user_input}", "green")
                    response = self.process_input(user_input)
                    
                    if response is None:
                        self.shutdown()
                        break
                    
                    self.respond(response)
                    
            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                log_message(f"Error in main loop: {e}", "error")
    
    def run_text_mode(self):
        """Run AVA in text input mode (for testing without microphone)."""
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
        farewell = f"Goodbye! It was nice talking to you. {self.name} signing off."
        print_colored(f"\n{self.name}: {farewell}", "cyan")
        self.tts.speak(farewell)
        
        summary = self.conversation.get_summary()
        print_colored(f"\nSession duration: {summary['duration']}", "magenta")
        print_colored(f"Total exchanges: {summary['exchanges']}", "magenta")
