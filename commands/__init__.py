"""Commands package for NEXA - extensible command system."""
from .base_command import BaseCommand, CommandRegistry
from .system_commands import TimeCommand, DateCommand, ExitCommand, OpenWebsiteCommand, HelpCommand
from .local_commands import (
    OpenAppCommand, CloseAppCommand, BrowserSearchCommand,
    PlayVideoCommand, VolumeControlCommand, SystemControlCommand, ScreenshotCommand
)
