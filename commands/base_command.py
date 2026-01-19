"""
Base Command System for AVA.
Provides extensible command handling for custom commands.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Callable
from utils.helpers import log_message


class BaseCommand(ABC):
    """Abstract base class for all commands."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the command."""
        pass
    
    @property
    @abstractmethod
    def triggers(self) -> List[str]:
        """List of phrases that trigger this command."""
        pass
    
    @property
    def description(self) -> str:
        """Description of what the command does."""
        return "No description available."
    
    @abstractmethod
    def execute(self, user_input: str) -> Optional[str]:
        """
        Execute the command.
        
        Args:
            user_input: The full user input that triggered the command
            
        Returns:
            Response string or None if command should pass to AI
        """
        pass


class CommandRegistry:
    """Registry for managing and executing commands."""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
        self._trigger_map: Dict[str, str] = {}  # trigger -> command name
    
    def register(self, command: BaseCommand) -> None:
        """Register a command."""
        self._commands[command.name] = command
        for trigger in command.triggers:
            self._trigger_map[trigger.lower()] = command.name
    
    def unregister(self, command_name: str) -> bool:
        """Unregister a command by name."""
        if command_name in self._commands:
            command = self._commands[command_name]
            for trigger in command.triggers:
                self._trigger_map.pop(trigger.lower(), None)
            del self._commands[command_name]
            return True
        return False
    
    def find_command(self, user_input: str) -> Optional[BaseCommand]:
        """Find a command that matches the user input."""
        user_input_lower = user_input.lower()
        
        for trigger, command_name in self._trigger_map.items():
            if trigger in user_input_lower:
                return self._commands[command_name]
        
        return None
    
    def execute(self, user_input: str) -> Optional[str]:
        """
        Find and execute a matching command.
        
        Returns:
            Response string or None if no command matched
        """
        command = self.find_command(user_input)
        if command:
            log_message(f"Executing command: {command.name}", "info")
            return command.execute(user_input)
        return None
    
    def list_commands(self) -> List[Dict[str, str]]:
        """List all registered commands."""
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "triggers": cmd.triggers
            }
            for cmd in self._commands.values()
        ]
