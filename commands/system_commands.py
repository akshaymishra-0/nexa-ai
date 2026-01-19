"""
Built-in system commands for AVA.
"""
import datetime
import webbrowser
from typing import Optional, List
from .base_command import BaseCommand


class TimeCommand(BaseCommand):
    """Command to tell the current time."""
    
    @property
    def name(self) -> str:
        return "time"
    
    @property
    def triggers(self) -> List[str]:
        return ["what time is it", "tell me the time", "current time", "what's the time"]
    
    @property
    def description(self) -> str:
        return "Tells the current time"
    
    def execute(self, user_input: str) -> Optional[str]:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."


class DateCommand(BaseCommand):
    """Command to tell the current date."""
    
    @property
    def name(self) -> str:
        return "date"
    
    @property
    def triggers(self) -> List[str]:
        return ["what's the date", "what date is it", "tell me the date", "today's date"]
    
    @property
    def description(self) -> str:
        return "Tells the current date"
    
    def execute(self, user_input: str) -> Optional[str]:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today is {current_date}."


class ExitCommand(BaseCommand):
    """Command to exit the assistant."""
    
    @property
    def name(self) -> str:
        return "exit"
    
    @property
    def triggers(self) -> List[str]:
        return ["goodbye", "bye", "exit", "quit", "stop", "shut down", "go to sleep"]
    
    @property
    def description(self) -> str:
        return "Exits the assistant"
    
    def execute(self, user_input: str) -> Optional[str]:
        return "__EXIT__"  # Special signal to exit


class OpenWebsiteCommand(BaseCommand):
    """Command to open websites."""
    
    @property
    def name(self) -> str:
        return "open_website"
    
    @property
    def triggers(self) -> List[str]:
        return ["open youtube", "open google", "open github", "open stackoverflow"]
    
    @property
    def description(self) -> str:
        return "Opens common websites"
    
    def execute(self, user_input: str) -> Optional[str]:
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "stackoverflow": "https://stackoverflow.com"
        }
        
        for site, url in websites.items():
            if site in user_input.lower():
                webbrowser.open(url)
                return f"Opening {site.capitalize()} for you."
        
        return None


class HelpCommand(BaseCommand):
    """Command to show available commands."""
    
    def __init__(self, registry):
        self.registry = registry
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def triggers(self) -> List[str]:
        return ["what can you do", "help me", "show commands", "list commands"]
    
    @property
    def description(self) -> str:
        return "Shows available commands"
    
    def execute(self, user_input: str) -> Optional[str]:
        commands = self.registry.list_commands()
        response = "Here's what I can do: "
        response += ", ".join([cmd["name"] for cmd in commands])
        response += ". I can also answer questions and have conversations!"
        return response


class ContinueCommand(BaseCommand):
    """Command to continue speaking the last response."""
    
    def __init__(self, tts_service):
        self.tts_service = tts_service
    
    @property
    def name(self) -> str:
        return "continue"
    
    @property
    def triggers(self) -> List[str]:
        return ["continue", "go on", "keep going", "resume", "continue speaking"]
    
    @property
    def description(self) -> str:
        return "Continues speaking the last response"
    
    def execute(self, user_input: str) -> Optional[str]:
        return "__CONTINUE__"  # Special signal to continue


class StopCommand(BaseCommand):
    """Command to stop speaking."""
    
    def __init__(self, tts_service):
        self.tts_service = tts_service
    
    @property
    def name(self) -> str:
        return "stop_speaking"
    
    @property
    def triggers(self) -> List[str]:
        return ["stop", "shut up", "be quiet", "silence", "enough", "okay stop"]
    
    @property
    def description(self) -> str:
        return "Stops AVA from speaking"
    
    def execute(self, user_input: str) -> Optional[str]:
        return "__STOP__"  # Special signal to stop
