import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print Klaus banner"""
    banner = r"""
     _  __ _       _     _ 
    | |/ /| |     | |   | |
    | ' / | |     | |   | |
    | . \ | |____ | |___| |
    |_|\_\|______| \_____/ 
    Knowledgeable Learning Assistant for Universal Support
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)