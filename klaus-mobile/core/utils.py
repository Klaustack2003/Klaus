import os
import sys
import platform

def is_android():
    """Detect Android reliably without Android-specific imports"""
    try:
        # Check common Android indicators
        if hasattr(sys, 'getandroidapilevel'):
            return True
        if 'ANDROID_BOOTLOGO' in os.environ:
            return True
        if 'ANDROID_ROOT' in os.environ and os.environ['ANDROID_ROOT'] == '/system':
            return True
        if platform.system().lower() == 'linux' and 'android' in sys.executable.lower():
            return True
        return False
    except:
        return False

def print_banner():
    banner = r"""
  _  __ _       _     _ 
 | |/ /| |     | |   | |
 | ' / | |     | |   | |
 | . \ | |____ | |___| |
 |_|\_\|______| \_____/ 
 Mobile Assistant
"""
    print(banner)

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)