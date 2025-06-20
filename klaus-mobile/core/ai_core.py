import os
import json
from datetime import datetime
from dotenv import load_dotenv
from .utils import is_android

try:
    import openai
    OPENAI_ENABLED = True
except ImportError:
    OPENAI_ENABLED = False

# Load environment variables - completely generic
def load_env():
    # First try standard .env location
    if os.path.exists('.env'):
        load_dotenv('.env')
    
    # Then try in app directory
    elif os.path.exists('assets/.env'):
        load_dotenv('assets/.env')
    
    # Android fallback
    elif is_android():
        try:
            # Generic Android file path
            env_path = '/data/data/org.klaus.klausai/files/.env'
            if os.path.exists(env_path):
                load_dotenv(env_path)
        except:
            pass

load_env()

class AICore:
    def __init__(self):
        self.context = self._load_context()
        self.max_history = 5
        
    def _load_context(self):
        return [
            {
                "role": "system", 
                "content": (
                    "You are Klaus, a helpful mobile AI assistant. "
                    "Keep responses concise and mobile-friendly. "
                    f"Today is {datetime.now().strftime('%A, %B %d')}."
                )
            }
        ]
    
    def process_query(self, user_input: str) -> str:
        self.context.append({"role": "user", "content": user_input})
        
        if not OPENAI_ENABLED or not os.getenv("OPENAI_API_KEY"):
            return "I'm offline right now. Try basic commands."
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.context,
                temperature=0.7,
                max_tokens=150
            )
            
            ai_reply = response.choices[0].message['content']
            self.context.append({"role": "assistant", "content": ai_reply})
            
            if len(self.context) > self.max_history:
                self.context = [self.context[0]] + self.context[-self.max_history+1:]
                
            return ai_reply
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"