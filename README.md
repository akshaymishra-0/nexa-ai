# AVA - Advanced Virtual Assistant

A personal AI voice assistant built with Python, similar to Jarvis. AVA can understand natural language, respond with voice, and execute commands.

## Features

- 🎤 **Voice Recognition**: Speak naturally to interact with AVA
- 🔊 **Text-to-Speech**: AVA responds with natural voice output
- 🤖 **AI-Powered**: Uses OpenRouter's free AI models for intelligent conversations
- 🔌 **Extensible Commands**: Easy to add custom commands
- 💬 **Context-Aware**: Maintains conversation history for context
- 🎨 **Beautiful CLI**: Colored console output for better readability

## Project Structure

```
AVA/
├── main.py                 # Entry point
├── .env                    # Environment variables (API keys)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── core/
│   ├── __init__.py
│   ├── assistant.py        # Main assistant logic
│   └── conversation.py     # Conversation management
├── services/
│   ├── __init__.py
│   ├── speech_recognition_service.py  # Speech to text
│   ├── text_to_speech_service.py      # Text to speech
│   └── ai_service.py       # OpenRouter AI integration
├── commands/
│   ├── __init__.py
│   ├── base_command.py     # Command framework
│   └── system_commands.py  # Built-in commands
└── utils/
    ├── __init__.py
    └── helpers.py          # Utility functions
```

## Installation

1. **Clone or navigate to the project**:
   ```bash
   cd AVA
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**:
   - Get a free API key from [OpenRouter](https://openrouter.ai/keys)
   - Edit `.env` file and add your API key:
     ```
     OPENROUTER_API_KEY=your_actual_api_key_here
     ```

## Usage

### Voice Mode (Default)
```bash
python main.py
```

### Text Mode (for testing)
```bash
python main.py --mode text
# or
python main.py -m text
```

## Built-in Commands

| Command | Triggers |
|---------|----------|
| Time | "what time is it", "tell me the time" |
| Date | "what's the date", "today's date" |
| Open Website | "open youtube", "open google", "open github" |
| Help | "what can you do", "help me" |
| Exit | "goodbye", "exit", "quit" |

## Adding Custom Commands

Create a new command by extending `BaseCommand`:

```python
# commands/my_commands.py
from commands.base_command import BaseCommand

class WeatherCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def triggers(self) -> list:
        return ["what's the weather", "weather forecast"]
    
    def execute(self, user_input: str) -> str:
        # Add your weather API logic here
        return "It's sunny today!"
```

Register it in `core/assistant.py`:
```python
from commands.my_commands import WeatherCommand
self.commands.register(WeatherCommand())
```

## Configuration Options

Edit `.env` file to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `AI_MODEL` | AI model to use | meta-llama/llama-3.2-3b-instruct:free |
| `ASSISTANT_NAME` | Name of the assistant | AVA |
| `WAKE_WORD` | Word to activate assistant | ava |
| `SPEECH_RATE` | Speech speed (100-300) | 175 |
| `SPEECH_VOLUME` | Volume level (0.0-1.0) | 1.0 |

## Free AI Models Available

OpenRouter offers several free models:
- `meta-llama/llama-3.2-3b-instruct:free` (default)
- `google/gemma-2-9b-it:free`
- `microsoft/phi-3-mini-128k-instruct:free`
- `mistralai/mistral-7b-instruct:free`

## Troubleshooting

### Microphone not working
- Ensure PyAudio is installed correctly
- On Windows, you may need to install PyAudio from wheel:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```

### API errors
- Verify your API key is correct in `.env`
- Check your internet connection
- Ensure you're using a free model if on free tier

## License

MIT License - Feel free to use and modify!

## Author

Akshay Mishra
