#!/usr/bin/env python3
"""
AVA - Advanced Virtual Assistant
A personal AI voice assistant built with Python.

Author: Akshay Mishra
"""
import sys
import argparse
from colorama import init

# Initialize colorama for Windows
init(autoreset=True)

from config.settings import settings
from core.assistant import Assistant
from utils.helpers import print_colored, log_message


def print_banner():
    """Print the AVA startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                   █████╗ ██╗   ██╗ █████╗                 ║
    ║                  ██╔══██╗██║   ██║██╔══██╗                ║
    ║                  ███████║██║   ██║███████║                ║
    ║                  ██╔══██║╚██╗ ██╔╝██╔══██║                ║
    ║                  ██║  ██║ ╚████╔╝ ██║  ██║                ║
    ║                  ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝                ║
    ║                                                           ║
    ║                 Advanced Virtual Assistant                ║
    ║                 Your Personal AI Companion                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print_colored(banner, "cyan")


def check_configuration():
    """Check if AVA is properly configured."""
    if not settings.validate():
        print_colored("\n⚠️  WARNING: OpenRouter API key not configured!", "yellow")
        print_colored("Please add your API key to the .env file.", "yellow")
        print_colored("Get your free API key at: https://openrouter.ai/keys\n", "cyan")
        return False
    return True


def main():
    """Main entry point for AVA."""
    parser = argparse.ArgumentParser(
        description="AVA - Advanced Virtual Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['voice', 'text'],
        default='voice',
        help='Run mode: voice (default) or text'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Print startup banner
    print_banner()
    
    # Check configuration
    check_configuration()
    
    try:
        # Create and run the assistant
        assistant = Assistant()
        
        if args.mode == 'voice':
            assistant.run_voice_mode()
        else:
            assistant.run_text_mode()
            
    except KeyboardInterrupt:
        print_colored("\n\nInterrupted by user.", "yellow")
        sys.exit(0)
    except Exception as e:
        log_message(f"Fatal error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
