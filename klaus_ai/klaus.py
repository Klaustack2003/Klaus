import time
from voice_interface import VoiceEngine
from ai_core import AICore
from skills import Skills
from memory import MemorySystem
from personality import PersonalityEngine
from utils import print_banner, clear_screen
import threading

WAKE_WORD = "hey klaus"
SLEEP_TIMEOUT = 30  # seconds of inactivity before sleeping

class Klaus:
    def __init__(self):
        self.voice = VoiceEngine(use_offline=False)  # Explicitly set mode
        self.ai = AICore()
        self.skills = Skills()
        self.memory = MemorySystem()
        self.personality = PersonalityEngine()
        self.active = False
        self.last_activity = time.time()
        
        # Load memory
        self.memory.load()
        self.ai.context = self.memory.get_recent_context(10)
        
    def wake(self):
        """Activate the assistant"""
        if not self.active:
            self.active = True
            self.voice.play_activation_sound()
            self.last_activity = time.time()
            print("Klaus Activated")
            
    def sleep(self):
        """Put assistant to sleep"""
        if self.active:
            self.active = False
            self.voice.speak("Going to sleep")
            print("Klaus Sleeping")
    
    def process_command(self, command):
        """Process user command"""
        self.last_activity = time.time()
        
        # Save interaction to memory
        self.memory.add_interaction(command, "")
        
        # First try skills system
        skill_response = self.skills.handle_command(command)
        
        if skill_response:
            if skill_response == "shutdown":
                self.voice.speak("Shutting down")
                self.memory.save()
                exit()
                
            # Apply personality to response
            final_response = self.personality.adjust_response(skill_response)
            self.voice.speak(final_response)
            self.memory.update_last_response(final_response)
        else:
            # Fallback to AI brain
            ai_response = self.ai.process_query(command)
            personality_response = self.personality.adjust_response(ai_response)
            self.voice.speak(personality_response)
            self.memory.update_last_response(personality_response)
    
    def run(self):
        """Main execution loop"""
        clear_screen()
        print_banner()
        print("Initializing Klaus System...")
        self.voice.speak("Klaus initialized. Say 'Hey Klaus' to activate me.")
        
        # Start continuous listening in background
        listener_thread = threading.Thread(target=self.continuous_listener)
        listener_thread.daemon = True
        listener_thread.start()
        
        while True:
            try:
                # Check for sleep timeout
                if self.active and time.time() - self.last_activity > SLEEP_TIMEOUT:
                    self.sleep()
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.voice.speak("Shutting down")
                self.memory.save()
                exit()
    
    def continuous_listener(self):
        """Background thread for continuous listening"""
        while True:
            if not self.active:
                # Low-power mode - check only for wake word
                user_input = self.voice.listen(timeout=1)
                if WAKE_WORD in user_input:
                    self.wake()
                    command = user_input.replace(WAKE_WORD, "").strip()
                    if command:
                        self.process_command(command)
            else:
                # Active mode - process all speech
                user_input = self.voice.listen(timeout=2)
                if user_input:
                    self.process_command(user_input)

if __name__ == "__main__":
    assistant = Klaus()
    assistant.run()