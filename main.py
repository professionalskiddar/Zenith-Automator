import os
import sys
import json
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item

# --- PATH HELPER FOR EXE ---
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    if relative_path.endswith(('.json', '.txt')):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(base_path, relative_path)

# --- CONFIGURATION PATHS ---
CONFIG_FILE = get_resource_path("config.json")
CHANNELS_FILE = get_resource_path("channels.json") 
DELAY_FILE = get_resource_path("delay.txt")

# --- COLOR PALETTE ---
COLOR_BG_MAIN = "#121212"        
COLOR_BG_PANEL = "#1E1E1E"      
COLOR_ACCENT_BLUE = "#007BFF"    
COLOR_TEXT_PRIMARY = "#FFFFFF"   
COLOR_TEXT_SECONDARY = "#B0B0B0" 
COLOR_CONSOLE_BG = "#000000"     
COLOR_CONSOLE_FG = "#00FF00"     
COLOR_CLOSE_HOVER = "#FF4B4B"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "discord_token": "",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "source_channel": "",
            "test_channel": ""
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def read_channels():
    if not os.path.exists(CHANNELS_FILE):
        initial = []
        with open(CHANNELS_FILE, "w") as f:
            json.dump(initial, f)
        return initial
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

def read_file_setting(file_path, default_val):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(str(default_val))
        return str(default_val)
    with open(file_path, "r") as f:
        return f.read().strip()

def save_file_setting(file_path, value):
    with open(file_path, "w") as f:
        f.write(str(value).strip())

class InteractiveTradeGUI:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True) 
        self.root.geometry("620x720") 
        self.root.configure(bg=COLOR_BG_MAIN)
        self.root.attributes("-topmost", True)
        
        self.offset_x = 0
        self.offset_y = 0

        try:
            icon_path = get_resource_path(os.path.join("assets", "icon.png"))
            img = Image.open(icon_path)
            self.app_icon = ImageTk.PhotoImage(img)
            self.root.iconphoto(False, self.app_icon)
            self.raw_icon_path = icon_path
        except Exception as e:
            print(f"Icon Error: {e}")
        
        self.engine_active = False 
        self.loop_count = 1
        self.countdown_seconds = 0
        self.target_channels = read_channels()
        self.channel_entries = [] 
        self.delay_val = read_file_setting(DELAY_FILE, "300")
        
        # --- CUSTOM TITLE BAR ---
        self.title_bar = tk.Frame(root, bg=COLOR_ACCENT_BLUE, height=40)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        self.title_label = tk.Label(self.title_bar, text="  ZENITH AUTOMATOR", 
                                    font=("Arial", 10, "bold"), fg="white", bg=COLOR_ACCENT_BLUE)
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.btn_close = tk.Button(self.title_bar, text="✕", command=self.exit_app, 
                                   bg=COLOR_ACCENT_BLUE, fg="white", bd=0, 
                                   font=("Arial", 12, "bold"), cursor="hand2", activebackground=COLOR_CLOSE_HOVER)
        self.btn_close.pack(side=tk.RIGHT, padx=5)

        self.btn_min = tk.Button(self.title_bar, text="—", command=self.hide_to_tray, 
                                  bg=COLOR_ACCENT_BLUE, fg="white", bd=0, 
                                  font=("Arial", 12, "bold"), cursor="hand2", activebackground="#0056b3")
        self.btn_min.pack(side=tk.RIGHT, padx=5)

        # --- STATUS HEADER ---
        self.status_header = tk.Frame(root, bg=COLOR_BG_MAIN, height=80)
        self.status_header.pack(fill=tk.X)
        
        self.lbl_status = tk.Label(self.status_header, text="Status: Stopped / Standby", 
                                    font=("Arial", 16, "bold"), fg="red", bg=COLOR_BG_MAIN)
        self.lbl_status.pack(pady=(15, 0))
        
        self.lbl_timer = tk.Label(self.status_header, text="Engine holding on standby.", 
                                  font=("Arial", 11), fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG_MAIN)
        self.lbl_timer.pack(pady=(0, 15))
        
        # --- MAIN BODY ---
        self.main_body = tk.Frame(root, bg=COLOR_BG_MAIN)
        self.main_body.pack(fill=tk.BOTH, expand=True, padx=20)

        btn_frame = tk.Frame(self.main_body, bg=COLOR_BG_MAIN)
        btn_frame.pack(pady=10)
        
        btn_style = {"font": ("Arial", 10, "bold"), "bd": 0, "cursor": "hand2"}
        
        self.btn_start = tk.Button(btn_frame, text="Start", width=10, command=self.start_engine, 
                                   bg="#2E7D32", fg="white", **btn_style)
        self.btn_start.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_stop = tk.Button(btn_frame, text="Stop", width=10, command=self.stop_engine, 
                                  state=tk.DISABLED, bg="#C62828", fg="white", **btn_style)
        self.btn_stop.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_restart = tk.Button(btn_frame, text="Restart", width=10, command=self.restart_engine, 
                                     bg="#455A64", fg="white", **btn_style)
        self.btn_restart.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_check = tk.Button(btn_frame, text="Check Latest", width=12, command=self.check_latest_message, 
                                   bg="#F9A825", fg="black", **btn_style)
        self.btn_check.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_test = tk.Button(btn_frame, text="Test Message", width=12, command=self.test_message_send, 
                                   bg="#6A1B9A", fg="white", **btn_style)
        self.btn_test.grid(row=1, column=1, padx=5, pady=5)

        self.btn_settings = tk.Button(btn_frame, text="Settings", width=12, command=self.launch_setup_wizard, 
                                      bg="#4A90E2", fg="white", **btn_style)
        self.btn_settings.grid(row=1, column=2, padx=5, pady=5)
        
        divider = tk.Frame(self.main_body, height=1, bg="#333333")
        divider.pack(fill=tk.X, pady=15)
        
        terminal_lbl = tk.Label(self.main_body, text="💻 Interactive Command Terminal", 
                                font=("Arial", 10, "bold"), fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG_MAIN)
        terminal_lbl.pack()
        
        self.txt_console = tk.Text(self.main_body, width=70, height=10, bg=COLOR_CONSOLE_BG, 
                                   fg=COLOR_CONSOLE_FG, font=("Consolas", 10), bd=0)
        self.txt_console.pack(pady=5)
        self.log_to_console("Type 'help' to see commands.") 
        self.txt_console.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(self.main_body, bg=COLOR_BG_MAIN)
        input_frame.pack(pady=5)
        
        prompt_lbl = tk.Label(input_frame, text=">>> ", font=("Consolas", 10, "bold"), 
                              fg=COLOR_CONSOLE_FG, bg=COLOR_BG_MAIN)
        prompt_lbl.grid(row=0, column=0)
        
        self.entry_cmd = tk.Entry(input_frame, width=50, font=("Consolas", 10), 
                                  bg=COLOR_BG_PANEL, fg="white", insertbackground="white", bd=0)
        self.entry_cmd.grid(row=0, column=1)
        self.entry_cmd.bind("<Return>", self.parse_terminal_command)
        
        divider2 = tk.Frame(self.main_body, height=1, bg="#333333")
        divider2.pack(fill=tk.X, pady=15)
        
        self.settings_label = tk.Label(self.main_body, text="⚙️ Destination Channels", 
                                        font=("Arial", 11, "bold"), fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_MAIN)
        self.settings_label.pack(anchor="w", pady=(0, 5))
        
        self.settings_container = tk.Frame(self.main_body, bg=COLOR_BG_MAIN)
        self.settings_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.settings_container, height=180, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.settings_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG_MAIN)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.channels_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BG_MAIN)
        self.channels_frame.pack(fill=tk.X)
        
        for cid in self.target_channels:
            self.add_channel_row(cid)
            
        self.add_channel_btn = tk.Button(self.scrollable_frame, text="+ Add Channel", 
                                         command=self.add_channel_row, bg="#2E7D32", fg="white", bd=0, cursor="hand2")
        self.add_channel_btn.pack(pady=10)
        
        delay_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BG_MAIN)
        delay_frame.pack(fill=tk.X, pady=10)
        tk.Label(delay_frame, text="Base Loop Delay (Sec):", fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG_MAIN).grid(row=0, column=0, sticky=tk.W)
        self.entry_delay = tk.Entry(delay_frame, width=10, bg=COLOR_BG_PANEL, fg="white", bd=0, insertbackground="white")
        self.entry_delay.insert(0, self.delay_val)
        self.entry_delay.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        self.btn_save = tk.Button(self.scrollable_frame, text="Apply All Changes", width=20, 
                                  command=self.apply_settings, bg=COLOR_ACCENT_BLUE, fg="white", bd=0, cursor="hand2")
        self.btn_save.pack(pady=10)
        
        self.check_initial_setup()
        self.update_engine_button_state()
        
        self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        self.tray_thread.start()
        
        threading.Thread(target=self.core_worker_loop, daemon=True).start()

    # --- CONFIG VALIDATION ---
    def update_engine_button_state(self):
        config = load_config()
        is_valid = bool(config.get("discord_token")) and bool(config.get("source_channel"))
        state = tk.NORMAL if is_valid else tk.DISABLED
        self.btn_start.config(state=state)
        self.btn_stop.config(state=tk.DISABLED if not self.engine_active else tk.NORMAL)
        self.btn_restart.config(state=state)

    def check_initial_setup(self):
        config = load_config()
        if not config.get("discord_token") or not config.get("source_channel"):
            self.launch_setup_wizard()

    def launch_setup_wizard(self):
        setup = tk.Toplevel(self.root)
        setup.title("First Time Setup")
        setup.geometry("450x380")
        setup.configure(bg=COLOR_BG_MAIN)
        setup.attributes("-topmost", True)
        
        tk.Label(setup, text="Welcome to Zenith Automator", font=("Arial", 12, "bold"), fg="white", bg=COLOR_BG_MAIN).pack(pady=15)
        
        # INFO BUTTON (Circular style)
        info_btn = tk.Button(setup, text="ℹ️ Info", command=self.show_info, 
                            bg=COLOR_ACCENT_BLUE, fg="white", bd=0, font=("Arial", 9, "bold"), 
                            cursor="hand2", width=8)
        info_btn.pack(pady=0)
        
        fields = [
            ("Discord Token:", "discord_token"),
            ("Source Channel ID:", "source_channel"),
            ("Test Channel ID (Optional):", "test_channel"),
            ("User Agent:", "user_agent")
        ]
        
        entries = {}
        config = load_config()
        
        for label_text, key in fields:
            frame = tk.Frame(setup, bg=COLOR_BG_MAIN)
            frame.pack(fill=tk.X, padx=40, pady=5)
            tk.Label(frame, text=label_text, fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG_MAIN).pack(side=tk.LEFT)
            ent = tk.Entry(frame, bg=COLOR_BG_PANEL, fg="white", bd=0)
            ent.insert(0, config.get(key, ""))
            ent.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
            entries[key] = ent

        def save_setup():
            token = entries["discord_token"].get().strip()
            source = entries["source_channel"].get().strip()
            
            if not token or not source:
                messagebox.showerror("Required Fields", "You must provide both a Discord Token and a Source Channel ID to proceed.")
                return
            
            cleaned_token = token.strip(" \"'()[]")
            new_config = {
                "discord_token": cleaned_token,
                "source_channel": source,
                "test_channel": entries["test_channel"].get().strip(),
                "user_agent": entries["user_agent"].get().strip()
            }
            save_config(new_config)
            messagebox.showinfo("Success", "Setup complete! You can now use the app.")
            self.update_engine_button_state()
            setup.destroy()

        tk.Button(setup, text="Save & Exit", command=save_setup, bg=COLOR_ACCENT_BLUE, fg="white", bd=0, font=("Arial", 10, "bold")).pack(pady=20)

    def show_info(self):
        info_win = tk.Toplevel(self.root)
        info_win.title("Setup Help")
        info_win.geometry("400x350")
        info_win.configure(bg=COLOR_BG_PANEL)
        info_win.attributes("-topmost", True)
        
        text = (
            "Discord Token: Your unique account key. "
            "Find it in browser developer tools (F12) under Application > Local storage > https://discord.com > token.\n\n"
            "Source Channel ID: The ID of the channel you are mirroring FROM.\n\n"
            "Test Channel ID: A channel you own to verify the bot is working. Not required to be filled in.\n\n"
            "User Agent: Your browser's identity string. Keeps you hidden from Discords anti automessaging shit."
        )
        
        tk.Label(info_win, text="How to fill the fields:", font=("Arial", 11, "bold"), 
                 fg=COLOR_ACCENT_BLUE, bg=COLOR_BG_PANEL).pack(pady=15)
        tk.Label(info_win, text=text, font=("Arial", 10), fg="white", bg=COLOR_BG_PANEL, 
                 justify=tk.LEFT, wraplength=350).pack(padx=20, pady=10)
        tk.Button(info_win, text="Got it!", command=info_win.destroy, bg=COLOR_ACCENT_BLUE, fg="white", bd=0).pack(pady=20)

    def setup_tray(self):
        try:
            image = Image.open(self.raw_icon_path)
            image = image.convert("RGBA")
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
            menu = (item('Show Window', self.show_window), item('Exit', self.exit_app))
            self.tray_icon = pystray.Icon("Zenith", image, "Zenith Automator", menu, default=True)
            self.tray_icon.run()
        except Exception as e:
            print(f"Tray Icon Error: {e}")

    def hide_to_tray(self):
        self.root.withdraw() 
        self.log_to_console("💤 App hidden to system tray.")

    def show_window(self, icon=None, item=None):
        self.root.after(0, self._perform_restore)

    def _perform_restore(self):
        self.root.deiconify()
        self.root.lift() 
        self.root.attributes("-topmost", True) 
        self.root.focus_force() 
        self.log_to_console("🚀 App restored from tray.")

    def exit_app(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.destroy()

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def add_channel_row(self, default_val=""):
        row = tk.Frame(self.channels_frame, bg=COLOR_BG_MAIN)
        row.pack(fill=tk.X, pady=2)
        ent = tk.Entry(row, width=35, bg=COLOR_BG_PANEL, fg="white", bd=0, insertbackground="white")
        ent.insert(0, default_val)
        ent.pack(side=tk.LEFT, padx=5)
        btn_rem = tk.Button(row, text="-", width=2, command=lambda r=row, e=ent: self.remove_channel_row(r, e), 
                            fg="#FF5252", bg=COLOR_BG_MAIN, bd=0, cursor="hand2")
        btn_rem.pack(side=tk.LEFT)
        self.channel_entries.append((row, ent))

    def remove_channel_row(self, row_widget, entry_widget):
        if len(self.channel_entries) > 1:
            row_widget.destroy()
            self.channel_entries.remove((row_widget, entry_widget))
        else:
            messagebox.showwarning("Warning", "You must have at least one target channel.")

    def log_to_console(self, text_string):
        self.txt_console.config(state=tk.NORMAL)
        self.txt_console.insert(tk.END, text_string + "\n")
        self.txt_console.see(tk.END)
        self.txt_console.config(state=tk.DISABLED)

    def parse_terminal_command(self, event=None):
        raw_cmd = self.entry_cmd.get().strip()
        self.entry_cmd.delete(0, tk.END)
        if not raw_cmd: return
        self.log_to_console(f">>> {raw_cmd}")
        cmd_norm = raw_cmd.lower()
        if cmd_norm == "help":
            self.log_to_console("📋 Commands: start, stop, restart, settings")
        elif cmd_norm == "start": self.start_engine()
        elif cmd_norm == "stop": self.stop_engine()
        elif cmd_norm == "restart": self.restart_engine()
        elif cmd_norm == "settings":
            self.log_to_console(f"⚙️ Channels: {len(self.target_channels)} | Delay: {self.delay_val}s")
        else:
            self.log_to_console(f"❌ Unknown Command: '{raw_cmd}'")

    def get_latest_message_data(self):
        try:
            config = load_config()
            source = config.get("source_channel")
            if not source: return None, None
            auth_headers = {"Authorization": str(config["discord_token"]).strip(), "User-Agent": str(config["user_agent"]).strip(), "Accept": "*/*"}
            url = f"https://discord.com/api/v9/channels/{source}/messages?limit=1"
            res = requests.get(url, headers=auth_headers)
            if res.status_code != 200: return None, None
            logs = res.json()
            if not logs or not isinstance(logs, list): return None, None
            msg = logs[0]
            return msg.get("content", ""), msg.get("attachments", [])
        except Exception:
            return None, None

    def send_payload_to_channel(self, text, attachments, target_channel):
        try:
            config = load_config()
            auth_headers = {"Authorization": str(config["discord_token"]).strip(), "User-Agent": str(config["user_agent"]).strip(), "Accept": "*/*"}
            url = f"https://discord.com/api/v9/channels/{target_channel}/messages"
            payload = {"content": text}
            files = None
            if attachments:
                target_file = attachments[0]
                download = requests.get(target_file.get("url"), headers={"User-Agent": config["user_agent"]})
                if download.status_code == 200:
                    files = {"file": (target_file.get("filename", "chart.png"), download.content, target_file.get("content_type", "image/png"))}
            res = requests.post(url, headers=auth_headers, data=payload, files=files)
            return res.status_code in (200, 201)
        except Exception:
            return False

    def check_latest_message(self):
        self.log_to_console("🔍 Fetching latest broadcast...")
        text, attachments = self.get_latest_message_data()
        if text is not None:
            filename = attachments[0].get("filename", "N/A") if attachments else "No File"
            self.log_to_console(f"📝 Content: {text}")
            self.log_to_console(f"📎 File: {filename}")
        else:
            self.log_to_console("❌ Failed to retrieve message. Check source channel ID.")

    def test_message_send(self):
        config = load_config()
        test_chan = config.get("test_channel")
        if not test_chan:
            self.log_to_console("❌ Error: Test channel not set in config.")
            return
        self.log_to_console(f"🧪 Testing send to {test_chan}...")
        text, attachments = self.get_latest_message_data()
        if text is not None:
            success = self.send_payload_to_channel(text, attachments, test_chan)
            if success: self.log_to_console("✅ Test Success: Message delivered.")
            else: self.log_to_console("❌ Test Failed: Discord rejected request.")
        else:
            self.log_to_console("❌ Test Failed: Could not fetch source message.")

    def start_engine(self):
        if not self.engine_active:
            self.engine_active = True
            self.lbl_status.config(text="Status: Active Running", fg="#B2FF59")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.log_to_console("▶️ Automation loop successfully engaged.")

    def stop_engine(self):
        if self.engine_active:
            self.engine_active = False
            self.countdown_seconds = 0
            self.lbl_status.config(text="Status: Stopped / Standby", fg="white")
            self.lbl_timer.config(text="Engine loop completely stopped.")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.log_to_console("⏸️ Automation loop suspended.")

    def restart_engine(self):
        self.log_to_console("🔄 Forcing instant cycle sequence reset...")
        self.countdown_seconds = 0
        self.loop_count = 1
        self.start_engine()

    def apply_settings(self):
        current_channels = [ent.get().strip() for row, ent in self.channel_entries if ent.get().strip()]
        delay_input = self.entry_delay.get().strip()
        if not current_channels or not delay_input.isdigit():
            messagebox.showerror("Error", "Please provide valid Channel IDs and an integer Delay value.")
            return
        save_channels(current_channels)
        save_file_setting(DELAY_FILE, delay_input)
        self.target_channels = current_channels 
        self.delay_val = delay_input
        self.log_to_console(f"✅ Settings Updated -> {len(current_channels)} Channels | Delay: {delay_input}s")
        messagebox.showinfo("Success", "All settings updated successfully!")

    def core_worker_loop(self):
        while True:
            if self.engine_active:
                self.lbl_timer.config(text=f"Cycle #{self.loop_count}: Scanning source...")
                text, attachments = self.get_latest_message_data()
                if text is not None:
                    for channel in self.target_channels:
                        success = self.send_payload_to_channel(text, attachments, channel)
                        if success:
                            self.log_to_console(f"📦 [Cycle #{self.loop_count}] Forwarded to {channel}")
                        else:
                            self.log_to_console(f"⚠️ [Cycle #{self.loop_count}] Failed for {channel}")
                else:
                    self.log_to_//console(f"⚠️ [Cycle #{self.loop_count}] No message found.")
                try:
                    base_delay = int(read_file_setting(DELAY_FILE, "300"))
                except ValueError:
                    base_delay = 60
                self.countdown_seconds = base_delay + random.randint(1, 5)
                while self.countdown_seconds > 0 and self.engine_active:
                    self.lbl_timer.config(text=f"⏳ Next cycle in {self.countdown_seconds} seconds...")
                    time.sleep(1)
                    self.countdown_seconds -= 1
                self.loop_count += 1
            else:
                time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveTradeGUI(root)
    root.mainloop()
