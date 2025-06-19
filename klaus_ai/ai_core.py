import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class AICore:
    def __init__(self):
        self.context = self.load_context()
        self.max_history = 20  # Maintain last 20 exchanges
        
    def load_context(self):
        """Initialize AI context with system prompt"""
        return [
            {
                "role": "system", 
                "content": (
                    "You are Klaus, an advanced AI assistant. Your personality is helpful, precise, "
                    "and efficient. Respond concisely but naturally. Today's date is "
                    f"{datetime.now().strftime('%A, %B %d, %Y')}. "
                    "You have access to various skills. When asked to perform tasks, "
                    "use the available functions or provide helpful information."
                )
            }
        ]
    
    def process_query(self, user_input):
        """Process user input through AI model"""
        # Add user input to context
        self.context.append({"role": "user", "content": user_input})
        
        try:
            # Use gpt-4-turbo for best results
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=self.context,
                temperature=0.7,
                max_tokens=300
            )
            
            ai_reply = response.choices[0].message['content']
            
            # Add AI response to context
            self.context.append({"role": "assistant", "content": ai_reply})
            
            # Maintain context size
            if len(self.context) > self.max_history:
                self.context = [self.context[0]] + self.context[-self.max_history+1:]
                
            return ai_reply
            
        except openai.error.OpenAIError as e:
            return f"Sorry, I encountered an error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"