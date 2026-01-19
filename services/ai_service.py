"""
AI Service for AVA.
Handles communication with OpenRouter API for AI responses.
"""
import requests
from typing import Optional, List, Dict
from utils.helpers import log_message
from config.settings import settings


class AIService:
    """Service for getting AI responses from OpenRouter."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.AI_MODEL
        self.system_prompt = settings.SYSTEM_PROMPT
        
        # Conversation history for context
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10  # Keep last 10 exchanges
    
    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """Build the messages array for the API request."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _update_history(self, user_message: str, assistant_response: str) -> None:
        """Update conversation history."""
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_response(self, user_message: str) -> Optional[str]:
        """
        Get AI response for a user message.
        
        Args:
            user_message: The user's input message
            
        Returns:
            AI response string or None if error
        """
        if not self.api_key or self.api_key == 'your_openrouter_api_key_here':
            log_message("OpenRouter API key not configured!", "error")
            return "I'm sorry, but my AI service is not configured. Please add your OpenRouter API key to the .env file."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",  # Required by OpenRouter
                "X-Title": "AVA Personal Assistant"
            }
            
            payload = {
                "model": self.model,
                "messages": self._build_messages(user_message),
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data['choices'][0]['message']['content']
                
                # Update conversation history
                self._update_history(user_message, assistant_message)
                return assistant_message
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                log_message(f"API Error: {response.status_code} - {error_msg}", "error")
                return f"I encountered an error: {error_msg}"
                
        except requests.exceptions.Timeout:
            log_message("Request timed out.", "error")
            return "I'm sorry, the request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            log_message(f"Network error: {e}", "error")
            return "I'm having trouble connecting to my brain. Please check your internet connection."
        except Exception as e:
            log_message(f"Unexpected error: {e}", "error")
            return "I encountered an unexpected error. Please try again."
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        log_message("Conversation history cleared.", "info")
    
    def change_model(self, model: str) -> None:
        """Change the AI model being used."""
        self.model = model
        log_message(f"AI model changed to: {model}", "info")
