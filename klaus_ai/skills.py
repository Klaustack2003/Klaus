import datetime
import webbrowser
import pyautogui
import wikipedia
import wolframalpha
import os
import requests
from dotenv import load_dotenv
import subprocess
import random

load_dotenv()

class Skills:
    def __init__(self):
        self.wolfram_client = wolframalpha.Client(os.getenv("WOLFRAM_APPID"))
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    
    def handle_command(self, command: str) -> str:
        """Process command and return response if handled"""
        command = command.lower()
        
        #email skills
        if "send email" in command or "email to" in command:
            return self.handle_email_command(command)
        # Time skills
        if "time" in command:
            return datetime.datetime.now().strftime("It's %I:%M %p")
        
        # Date skills
        if "date" in command or "today" in command:
            return datetime.datetime.now().strftime("Today is %A, %B %d, %Y")
        
        # Web skills
        if "open youtube" in command:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube"
        
        if "open google" in command:
            webbrowser.open("https://google.com")
            return "Opening Google"
        
        if "search for" in command:
            query = command.split("search for")[-1].strip()
            webbrowser.open(f"https://google.com/search?q={query}")
            return f"Searching for {query}"
        
        # Calculation skills
        if "calculate" in command or any(op in command for op in ["+", "-", "*", "/"]):
            try:
                # Extract math expression
                expr = command.replace("calculate", "").strip()
                # Simple eval for testing (note: security risk for production!)
                result = str(eval(expr))  # Only for testing!
                return f"The result is {result}"
            except:
                # Fallback to Wolfram
                try:
                    res = self.wolfram_client.query(command)
                    return next(res.results).text
                except:
                    return "I couldn't calculate that"
        
        # Wikipedia skills
        if "wikipedia" in command or "who is" in command or "what is" in command:
            term = command.replace("wikipedia", "").replace("search", "").strip()
            try:
                summary = wikipedia.summary(term, sentences=2)
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Multiple results: {', '.join(e.options[:3])}"
            except:
                return "I couldn't find information on that topic"
        
        # System control
        if "screenshot" in command:
            pyautogui.screenshot().save("screenshot.png")
            return "Screenshot saved"
            
        if "shutdown" in command or "turn off" in command:
            return "shutdown"
            
        # Weather skills
        if "weather" in command:
            return self.get_weather(command)
        
        # Jokes
        if "tell me a joke" in command:
            return self.tell_joke()
            
        return ""
    
    def get_weather(self, command):
        """Get weather information using OpenWeatherMap API"""
        # Extract location
        location = "London"  # Default
        if "in" in command:
            location = command.split("in")[-1].strip()
        
        if not self.weather_api_key:
            return "Weather API not configured"
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"Weather in {location.title()}: {temp}°C, {desc}"
            else:
                return "Couldn't retrieve weather information"
        except:
            return "Weather service unavailable"
    
    def tell_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What did one ocean say to the other ocean? Nothing, they just waved!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "How does a penguin build its house? Igloos it together!"
        ]
        return random.choice(jokes)
    
    def open_app(self, app_name):
        """Open applications (Windows implementation)"""
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "chrome.exe",
            "word": "winword.exe",
            "excel": "excel.exe"
        }
        
        if app_name in apps:
            try:
                subprocess.Popen(apps[app_name])
                return f"Opening {app_name}"
            except:
                return f"Couldn't open {app_name}"
        return ""
    
    def handle_email_command(self, command):
        try:
            if "send email to" in command:
                parts = command.split("send email to")[1].strip().split("about")
                recipient = parts[0].strip()
                
                # Validate email format
                if not "@" in recipient:
                    return "Invalid email format"
                    
                content = parts[1].strip() if len(parts) > 1 else "No content"
                return f"Preparing email to {recipient}"  # Test response
                
            return ""
        except Exception as e:
            return f"Email error: {str(e)}"