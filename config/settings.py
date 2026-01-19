"""
Settings configuration for AVA.
Loads environment variables and provides centralized configuration.
"""
import os
from dotenv import load_dotenv
from pathlib import Path


class Settings:
    """Centralized settings management for AVA."""
    
    def __init__(self):
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # OpenRouter Configuration
        self.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
        self.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        
        # AI Model Configuration (using free models)
        self.AI_MODEL = os.getenv('AI_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
        
        # Assistant Configuration
        self.ASSISTANT_NAME = os.getenv('ASSISTANT_NAME', 'AVA')
        self.WAKE_WORD = os.getenv('WAKE_WORD', 'ava').lower()
        
        # Speech Settings
        self.SPEECH_RATE = int(os.getenv('SPEECH_RATE', 175))
        self.SPEECH_VOLUME = float(os.getenv('SPEECH_VOLUME', 1.0))
        
        # Creator info
        self.CREATOR_NAME = "Akshay"
        
        # System prompt for the AI
        self.SYSTEM_PROMPT = f"""You are {self.ASSISTANT_NAME}, a personal AI voice assistant created by {self.CREATOR_NAME}.

IMPORTANT RULES FOR YOUR RESPONSES:
1. You will be speaking aloud, so write responses that sound natural when spoken.
2. NEVER use markdown formatting like asterisks (*), bullet points, or numbered lists.
3. NEVER include URLs, links, or web addresses in your responses.
4. NEVER use emojis or special symbols.
5. Keep responses concise - 2-3 sentences maximum for simple questions.
6. Use natural conversational language, like talking to a friend.
7. Avoid technical jargon unless specifically asked.
8. When listing things, say them naturally like "first... second... and third" instead of using bullet points.

Your personality:
- Friendly, warm, and helpful like Jarvis from Iron Man
- Witty but professional
- Speak in a natural, human way
- Be confident and knowledgeable

When asked who you are: You are {self.ASSISTANT_NAME}, a personal AI assistant.
When asked who created/built you: You were created by {self.CREATOR_NAME}."""

    def validate(self) -> bool:
        """Validate that all required settings are configured."""
        if not self.OPENROUTER_API_KEY or self.OPENROUTER_API_KEY == 'your_openrouter_api_key_here':
            return False
        return True


# Global settings instance
settings = Settings()
