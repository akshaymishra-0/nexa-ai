"""
Local System Commands for NEXA.
Handles system operations like opening/closing apps, playing videos, browser control, etc.
"""
import subprocess
import os
import webbrowser
from .base_command import BaseCommand
from utils.helpers import log_message


class OpenAppCommand(BaseCommand):
    """Command to open applications."""
    
    APPS = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "files": "explorer.exe",
        "task manager": "taskmgr.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "steam": "steam.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "vs code": "code.exe",
        "vscode": "code.exe",
        "visual studio code": "code.exe",
        "vlc": "vlc.exe",
        "media player": "wmplayer.exe",
        "windows media player": "wmplayer.exe",
        "photos": "ms-photos:",
        "camera": "microsoft.windows.camera:",
        "mail": "outlookmail:",
        "calendar": "outlookcal:",
        "store": "ms-windows-store:",
        "xbox": "xbox:",
        "clock": "ms-clock:",
        "weather": "msnweather:",
        "maps": "bingmaps:",
        "snipping tool": "snippingtool.exe",
        "screenshot": "snippingtool.exe",
    }
    
    @property
    def name(self) -> str:
        return "open_app"
    
    @property
    def triggers(self) -> list:
        return ["open", "launch", "start", "run"]
    
    @property
    def description(self) -> str:
        return "Opens applications on your computer"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        if not any(trigger in user_input_lower for trigger in ["open", "launch", "start", "run"]):
            return None
        
        for app_name, app_path in self.APPS.items():
            if app_name in user_input_lower:
                try:
                    if app_path.endswith(":"):
                        os.startfile(app_path)
                    else:
                        subprocess.Popen(app_path, shell=True)
                    log_message(f"Opened: {app_name}", "success")
                    return f"Opening {app_name} for you."
                except Exception as e:
                    log_message(f"Error opening {app_name}: {e}", "error")
                    return f"Sorry, I couldn't open {app_name}. It might not be installed."
        
        return None


class CloseAppCommand(BaseCommand):
    """Command to close applications."""
    
    PROCESS_NAMES = {
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
        "paint": "mspaint.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "spotify": "Spotify.exe",
        "discord": "Discord.exe",
        "steam": "steam.exe",
        "vs code": "Code.exe",
        "vscode": "Code.exe",
        "visual studio code": "Code.exe",
        "vlc": "vlc.exe",
        "media player": "wmplayer.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "task manager": "Taskmgr.exe",
        "browser": "msedge.exe",
        "all browsers": ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe", "opera.exe"],
    }
    
    @property
    def name(self) -> str:
        return "close_app"
    
    @property
    def triggers(self) -> list:
        return ["close", "kill", "stop", "terminate", "end"]
    
    @property
    def description(self) -> str:
        return "Closes applications on your computer"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        if not any(trigger in user_input_lower for trigger in ["close", "kill", "stop", "terminate", "end"]):
            return None
        
        if any(word in user_input_lower for word in ["goodbye", "bye", "nexa", "assistant"]):
            return None
        
        for app_name, process in self.PROCESS_NAMES.items():
            if app_name in user_input_lower:
                try:
                    if isinstance(process, list):
                        for proc in process:
                            subprocess.run(f'taskkill /F /IM {proc}', shell=True, capture_output=True)
                        return f"Closing all {app_name}."
                    else:
                        result = subprocess.run(f'taskkill /F /IM {process}', shell=True, capture_output=True)
                        if result.returncode == 0:
                            return f"Closed {app_name}."
                        else:
                            return f"{app_name.capitalize()} doesn't seem to be running."
                except Exception as e:
                    log_message(f"Error closing {app_name}: {e}", "error")
                    return f"Sorry, I couldn't close {app_name}."
        
        return None


class BrowserSearchCommand(BaseCommand):
    """Command to search in browser."""
    
    @property
    def name(self) -> str:
        return "browser_search"
    
    @property
    def triggers(self) -> list:
        return ["search for", "google", "look up", "find me", "search", "browse"]
    
    @property
    def description(self) -> str:
        return "Searches for something in your browser"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        search_query = None
        
        patterns = ["search for ", "google ", "look up ", "find me ", "search ", "browse for ", "browse "]
        
        for pattern in patterns:
            if pattern in user_input_lower:
                idx = user_input_lower.find(pattern)
                search_query = user_input[idx + len(pattern):].strip()
                break
        
        if search_query:
            for ending in [" on google", " on the internet", " online", " on web"]:
                if search_query.lower().endswith(ending):
                    search_query = search_query[:-len(ending)]
            
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            webbrowser.open(search_url)
            log_message(f"Searching for: {search_query}", "success")
            return f"Searching for {search_query} on Google."
        
        return None


class PlayVideoCommand(BaseCommand):
    """Command to play videos from YouTube."""
    
    @property
    def name(self) -> str:
        return "play_video"
    
    @property
    def triggers(self) -> list:
        return ["play", "play video", "play music", "play song", "watch"]
    
    @property
    def description(self) -> str:
        return "Plays videos or music from YouTube"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        if not any(trigger in user_input_lower for trigger in ["play", "watch"]):
            return None
        
        query = None
        patterns = ["play video ", "play music ", "play song ", "play ", "watch "]
        
        for pattern in patterns:
            if pattern in user_input_lower:
                idx = user_input_lower.find(pattern)
                query = user_input[idx + len(pattern):].strip()
                break
        
        if query:
            for phrase in [" on youtube", " video", " from youtube"]:
                if query.lower().endswith(phrase):
                    query = query[:-len(phrase)]
            
            youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(youtube_url)
            log_message(f"Playing: {query}", "success")
            return f"Searching for {query} on YouTube."
        
        return None


class VolumeControlCommand(BaseCommand):
    """Command to control system volume."""
    
    @property
    def name(self) -> str:
        return "volume_control"
    
    @property
    def triggers(self) -> list:
        return ["volume", "mute", "unmute", "louder", "quieter", "sound"]
    
    @property
    def description(self) -> str:
        return "Controls system volume"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        try:
            if "mute" in user_input_lower and "unmute" not in user_input_lower:
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"', 
                             shell=True, capture_output=True)
                return "System muted."
            
            elif "unmute" in user_input_lower:
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"', 
                             shell=True, capture_output=True)
                return "System unmuted."
            
            elif any(word in user_input_lower for word in ["increase", "up", "louder", "higher", "raise"]):
                for _ in range(5):
                    subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"', 
                                 shell=True, capture_output=True)
                return "Volume increased."
            
            elif any(word in user_input_lower for word in ["decrease", "down", "quieter", "lower", "reduce"]):
                for _ in range(5):
                    subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"', 
                                 shell=True, capture_output=True)
                return "Volume decreased."
            
            elif "max" in user_input_lower or "full" in user_input_lower:
                for _ in range(20):
                    subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"', 
                                 shell=True, capture_output=True)
                return "Volume set to maximum."
            
        except Exception as e:
            log_message(f"Error controlling volume: {e}", "error")
            return "Sorry, I couldn't control the volume."
        
        return None


class SystemControlCommand(BaseCommand):
    """Command for system operations like shutdown, restart, sleep."""
    
    @property
    def name(self) -> str:
        return "system_control"
    
    @property
    def triggers(self) -> list:
        return ["shutdown", "restart", "sleep", "lock", "log off", "hibernate"]
    
    @property
    def description(self) -> str:
        return "Controls system power options"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        try:
            if "shutdown" in user_input_lower or "shut down" in user_input_lower:
                return "For safety, please use the Start menu to shutdown. Say 'yes shutdown' to confirm."
            
            elif "restart" in user_input_lower:
                return "For safety, please use the Start menu to restart. Say 'yes restart' to confirm."
            
            
        except Exception as e:
            log_message(f"Error with system control: {e}", "error")
            return "Sorry, I couldn't perform that action."
        
        return None


class ScreenshotCommand(BaseCommand):
    """Command to take screenshots."""
    
    @property
    def name(self) -> str:
        return "screenshot"
    
    @property
    def triggers(self) -> list:
        return ["screenshot", "screen shot", "capture screen", "take a screenshot", "snip"]
    
    @property
    def description(self) -> str:
        return "Takes a screenshot"
    
    def execute(self, user_input: str):
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["screenshot", "screen shot", "capture screen", "snip"]):
            try:
                subprocess.Popen('snippingtool.exe', shell=True)
                return "Opening the snipping tool. Select the area you want to capture."
            except:
                try:
                    subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys(\'^+s\')"', 
                                 shell=True, capture_output=True)
                    return "Opening screenshot tool. Select the area you want to capture."
                except Exception as e:
                    log_message(f"Error taking screenshot: {e}", "error")
                    return "Sorry, I couldn't open the screenshot tool."
        
        return None
