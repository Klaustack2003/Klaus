import json
import os
from datetime import datetime

class MemorySystem:
    def __init__(self):
        self.memory_file = "klaus_memory.json"
        self.context = []
        
    def load(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.context = json.load(f)
                print(f"Loaded memory with {len(self.context)} items")
            else:
                self.context = []
                print("No memory file found, starting fresh")
        except:
            self.context = []
            print("Error loading memory, starting fresh")
    
    def save(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.context, f)
            print("Memory saved successfully")
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
    
    def add_interaction(self, user_input, ai_response):
        """Add new interaction to memory"""
        self.context.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "klaus": ai_response
        })
        
        # Keep only the last 100 interactions
        if len(self.context) > 100:
            self.context = self.context[-100:]
    
    def update_last_response(self, response):
        """Update the last interaction with Klaus's response"""
        if self.context:
            self.context[-1]["klaus"] = response
    
    def get_recent_context(self, count=5):
        """Get recent conversations for context"""
        recent = self.context[-count:]
        return [{"role": "user", "content": item["user"]} for item in recent]