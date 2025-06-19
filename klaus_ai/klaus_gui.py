import tkinter as tk
from tkinter import ttk, scrolledtext, PhotoImage
from PIL import Image, ImageTk
import threading
import queue
from voice_interface import VoiceEngine
from ai_core import AICore
from skills import Skills
import time
import os

class KlausGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Klaus AI Assistant")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize Klaus components
        self.voice = VoiceEngine()
        self.ai = AICore()
        self.skills = Skills()
        self.message_queue = queue.Queue()
        
        # GUI state variables
        self.listening = False
        self.thinking = False
        
        # Configure styles
        self.setup_styles()
        
        # Build interface
        self.create_widgets()
        
        # Start message processing thread
        self.process_message_thread()
        
        # Start periodic UI updates
        self.update_ui()

    def setup_styles(self):
        """Configure modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.bg_color = "#2d2d2d"
        self.fg_color = "#ffffff"
        self.accent_color = "#4a90e2"
        self.secondary_color = "#3d3d3d"
        
        # Configure styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', 
                       background=self.accent_color, 
                       foreground=self.fg_color,
                       borderwidth=0,
                       focuscolor=self.bg_color)
        style.map('TButton',
                  background=[('active', self.secondary_color)],
                  foreground=[('active', self.fg_color)])
        
        style.configure('TEntry', 
                       fieldbackground=self.secondary_color,
                       foreground=self.fg_color,
                       insertcolor=self.fg_color)
        
        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """Create all GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Load and display logo
        try:
            logo_img = Image.open("assets/klaus_logo.png").resize((40, 40))
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=self.logo)
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            # Fallback if no logo
            pass
            
        ttk.Label(header_frame, 
                 text="Klaus AI Assistant", 
                 font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        self.status_indicator = ttk.Label(header_frame, 
                                        textvariable=self.status_var,
                                        foreground="#aaaaaa")
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            bg=self.secondary_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            font=('Segoe UI', 11),
            padx=10,
            pady=10,
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.user_input = ttk.Entry(
            input_frame,
            font=('Segoe UI', 11)
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind('<Return>', self.send_text_message)
        
        # Voice button
        self.voice_button_img = self.create_voice_button_image()
        self.voice_button = ttk.Button(
            input_frame,
            image=self.voice_button_img,
            command=self.toggle_voice_recognition,
            style='TButton'
        )
        self.voice_button.pack(side=tk.RIGHT)
        
        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_text_message,
            style='TButton'
        )
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Settings menu
        self.create_menu()

    def create_voice_button_image(self):
        """Create dynamic voice button image"""
        img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferences")
        settings_menu.add_command(label="Voice Settings")
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About Klaus")
        help_menu.add_command(label="Documentation")
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def toggle_voice_recognition(self):
        """Toggle voice listening state"""
        if not self.listening:
            self.listening = True
            self.status_var.set("Listening...")
            threading.Thread(target=self.voice_listen_thread, daemon=True).start()
        else:
            self.listening = False
            self.status_var.set("Ready")

    def voice_listen_thread(self):
        """Thread for voice recognition"""
        while self.listening:
            text = self.voice.listen(timeout=2)
            if text:
                self.message_queue.put(('user', text))
                self.process_command(text)
            time.sleep(0.1)
        
        self.status_var.set("Ready")

    def send_text_message(self, event=None):
        """Send text message from input box"""
        text = self.user_input.get()
        if text.strip():
            self.message_queue.put(('user', text))
            self.user_input.delete(0, tk.END)
            self.process_command(text)

    def process_command(self, command):
        """Process user command"""
        self.thinking = True
        self.status_var.set("Thinking...")
        
        # Process in background thread
        threading.Thread(
            target=self.process_command_thread,
            args=(command,),
            daemon=True
        ).start()

    def process_command_thread(self, command):
        """Thread for processing commands"""
        # First try skills system
        skill_response = self.skills.handle_command(command)
        
        if skill_response:
            if skill_response == "shutdown":
                self.message_queue.put(('system', "Shutting down"))
                self.root.after(1000, self.root.quit)
            else:
                self.message_queue.put(('klaus', skill_response))
        else:
            # Fallback to AI brain
            ai_response = self.ai.process_query(command)
            self.message_queue.put(('klaus', ai_response))
        
        self.thinking = False
        self.status_var.set("Ready")

    def process_message_thread(self):
        """Process messages from queue"""
        try:
            while True:
                msg_type, msg_content = self.message_queue.get_nowait()
                
                self.chat_display.configure(state='normal')
                
                if msg_type == 'user':
                    self.chat_display.insert(tk.END, "You: ", 'user_tag')
                    self.chat_display.insert(tk.END, msg_content + "\n\n", 'user_msg')
                elif msg_type == 'klaus':
                    self.chat_display.insert(tk.END, "Klaus: ", 'klaus_tag')
                    self.chat_display.insert(tk.END, msg_content + "\n\n", 'klaus_msg')
                else:  # system
                    self.chat_display.insert(tk.END, msg_content + "\n", 'system_msg')
                
                self.chat_display.configure(state='disabled')
                self.chat_display.see(tk.END)
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_message_thread)

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.configure(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state='disabled')

    def update_ui(self):
        """Update UI elements periodically"""
        # Update voice button color based on listening state
        if self.listening:
            self.voice_button.configure(style='Accent.TButton')
        else:
            self.voice_button.configure(style='TButton')
        
        # Update thinking indicator
        if self.thinking:
            current_status = self.status_var.get()
            if "..." in current_status:
                dots = len(current_status.split(".")) - 1
                new_status = "Thinking" + "." * ((dots % 3) + 1)
                self.status_var.set(new_status)
        
        self.root.after(300, self.update_ui)

    def run(self):
        """Run the application"""
        # Initialize text tags for styling
        self.chat_display.tag_configure('user_tag', foreground="#4a90e2", font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_configure('user_msg', foreground="#ffffff")
        self.chat_display.tag_configure('klaus_tag', foreground="#2ecc71", font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_configure('klaus_msg', foreground="#eeeeee")
        self.chat_display.tag_configure('system_msg', foreground="#aaaaaa", font=('Segoe UI', 9))

        # Add welcome message (fixed version)
        welcome_msg = (
            "Klaus AI Assistant initialized.\n"
            "Type your message or click the microphone button to speak.\n\n"
            "Try commands like:\n"
            "- What's the weather in London?\n"
            "- Calculate 15% of 200\n"
            "- Tell me a joke\n"
            "- Search for AI news\n\n"
        )
        self.message_queue.put(('system', welcome_msg))
        
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = KlausGUI(root)
    app.run()