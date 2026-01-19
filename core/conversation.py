"""
Conversation Manager for AVA.
Handles conversation flow and context management.
"""
from typing import List, Dict, Optional
from datetime import datetime
from utils.helpers import log_message


class ConversationManager:
    """Manages conversation state and context."""
    
    def __init__(self, max_context_length: int = 20):
        self.max_context_length = max_context_length
        self.conversation_log: List[Dict] = []
        self.session_start = datetime.now()
        self.user_name: Optional[str] = None
    
    def add_exchange(self, user_input: str, assistant_response: str) -> None:
        """Add a conversation exchange to the log."""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response
        }
        self.conversation_log.append(exchange)
        
        # Trim if exceeds max length
        if len(self.conversation_log) > self.max_context_length:
            self.conversation_log = self.conversation_log[-self.max_context_length:]
    
    def get_context(self) -> List[Dict]:
        """Get the conversation context."""
        return self.conversation_log
    
    def get_session_duration(self) -> str:
        """Get the duration of the current session."""
        duration = datetime.now() - self.session_start
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        
        if minutes > 0:
            return f"{minutes} minutes and {seconds} seconds"
        return f"{seconds} seconds"
    
    def set_user_name(self, name: str) -> None:
        """Set the user's name for personalization."""
        self.user_name = name
        log_message(f"User name set to: {name}", "info")
    
    def clear_context(self) -> None:
        """Clear the conversation context."""
        self.conversation_log = []
        log_message("Conversation context cleared.", "info")
    
    def get_summary(self) -> Dict:
        """Get a summary of the conversation session."""
        return {
            "session_start": self.session_start.isoformat(),
            "duration": self.get_session_duration(),
            "exchanges": len(self.conversation_log),
            "user_name": self.user_name
        }
