from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from core.voice_interface import VoiceEngine
from core.ai_core import AICore
from core.skills import Skills
from core.utils import is_android, print_banner
import threading
import os

Builder.load_string('''
<KlausMobile>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    BoxLayout:
        size_hint_y: 0.1
        Label:
            text: 'Klaus AI Assistant'
            font_size: 24
            bold: True
            color: 0.2, 0.6, 1, 1
    
    ScrollView:
        id: scroll
        size_hint_y: 0.7
        TextInput:
            id: chat_log
            readonly: True
            background_color: 0.1, 0.1, 0.1, 1
            foreground_color: 1, 1, 1, 1
            size_hint_y: None
            height: max(self.minimum_height, scroll.height)
            font_size: 16
    
    BoxLayout:
        size_hint_y: 0.2
        spacing: 10
        
        TextInput:
            id: user_input
            hint_text: 'Type command or tap mic...'
            multiline: False
            font_size: 18
            background_color: 0.2, 0.2, 0.2, 1
            foreground_color: 1, 1, 1, 1
            padding: [10, 10]
        
        Button:
            id: mic_btn
            text: '🎤'
            font_size: 24
            size_hint_x: 0.2
            background_color: 0.3, 0.7, 1, 1
            on_press: root.toggle_listen()
            
        Button:
            id: send_btn
            text: 'Send'
            size_hint_x: 0.2
            background_color: 0.2, 0.8, 0.4, 1
            on_press: root.send_text()
''')

class KlausMobile(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voice = VoiceEngine(use_offline=True)
        self.ai = AICore()
        self.skills = Skills()
        self.listening = False
        self.update_chat("Klaus Mobile initialized\nTap mic to speak")
    
    def toggle_listen(self):
        if not self.listening:
            self.ids.mic_btn.text = "🔴"
            self.ids.mic_btn.background_color = (1, 0.2, 0.2, 1)
            threading.Thread(target=self.listen_thread, daemon=True).start()
        else:
            self.ids.mic_btn.text = "🎤"
            self.ids.mic_btn.background_color = (0.3, 0.7, 1, 1)
            self.listening = False
            
    def send_text(self):
        text = self.ids.user_input.text.strip()
        if text:
            self.ids.user_input.text = ""
            self.process_command(text)
            
    def listen_thread(self):
        self.listening = True
        self.update_chat("\nListening... (Speak now)")
        
        success, text = self.voice.listen(timeout=10)
        
        Clock.schedule_once(lambda dt: self.finish_listening(success, text))
    
    def finish_listening(self, success, text):
        self.ids.mic_btn.text = "🎤"
        self.ids.mic_btn.background_color = (0.3, 0.7, 1, 1)
        self.listening = False
        
        if success and text:
            self.process_command(text)
        elif success:
            self.update_chat("\nHeard nothing, try again")
        else:
            self.update_chat("\nListening failed")
        
    def process_command(self, command):
        self.update_chat(f"\n\nYou: {command}")
        
        # Process command
        skill_response = self.skills.handle_command(command)
        if skill_response:
            response = skill_response
        else:
            response = self.ai.process_query(command)
            
        self.update_chat(f"\nKlaus: {response}")
        self.voice.speak(response)
        
    def update_chat(self, text):
        self.ids.chat_log.text += text
        # Auto-scroll to bottom
        self.ids.scroll.scroll_y = 0

class KlausApp(App):
    def build(self):
        return KlausMobile()
    
    def on_start(self):
        print_banner()

if __name__ == '__main__':
    KlausApp().run()