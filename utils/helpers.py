"""
Helper utilities for AVA.
"""
import re
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init(autoreset=True)


def clean_text_for_speech(text: str) -> str:
    """
    Clean text to make it suitable for text-to-speech.
    Preserves emotion markers [happy], [sad] etc for TTS processing.
    Removes markdown, links, emojis, and other non-speakable content.
    """
    if not text:
        return text
    
    # Preserve emotion markers at the start - don't remove them
    # The TTS service will handle these
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Remove markdown bold/italic (**, *, __, _)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove markdown headers (#)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove markdown code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove markdown links [text](url) but NOT emotion markers like [happy]
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove bullet points and list markers
    text = re.sub(r'^[\s]*[-*•]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Remove emojis and special unicode characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but preserve emotion markers in brackets
    text = re.sub(r'[<>{}|\\^~]', '', text)
    
    return text.strip()


def print_colored(message: str, color: str = "white", prefix: str = "") -> None:
    """Print colored text to console."""
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    
    color_code = colors.get(color.lower(), Fore.WHITE)
    if prefix:
        print(f"{color_code}{prefix} {message}{Style.RESET_ALL}")
    else:
        print(f"{color_code}{message}{Style.RESET_ALL}")


def log_message(message: str, level: str = "info") -> None:
    """Log a message with timestamp and level."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    level_colors = {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "debug": "magenta"
    }
    
    level_prefixes = {
        "info": "[INFO]",
        "success": "[SUCCESS]",
        "warning": "[WARNING]",
        "error": "[ERROR]",
        "debug": "[DEBUG]"
    }
    
    color = level_colors.get(level.lower(), "white")
    prefix = level_prefixes.get(level.lower(), "[LOG]")
    
    print_colored(f"[{timestamp}] {message}", color, prefix)


def get_greeting() -> str:
    """Get appropriate greeting based on time of day."""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Hello"
