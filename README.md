# ⚡ Zenith Automator

**Zenith Automator** is a Discord message mirroring tool. It is designed to monitor a specific private source channel and instantly forward trading alerts, text, and visual charts to one or multiple destination channels.

## ✨ Key Features

- **🚀 Multi-Channel Mirroring**: Forward a single source alert to an unlimited number of destination channels.
- **🕒 Human-Jitter Timing**: Implements a random 1–5 second "fuzzing" delay on top of your base cooldown to mimic human behavior and avoid detection.
- **🖼️ Asset Forwarding**: Automatically detects and clones image attachments (charts) along with the text content.
- **🌙 Zenith Dark Edition**: A fully custom, frameless, dark-themed GUI with a custom title bar and a professional look.
- **🔋 System Tray Integration**: Minimize the app to the system tray to keep it running in the background without cluttering your taskbar.
- **🔝 Always-on-Top**: Keeps the controller visible at all times so you can monitor cycles and status updates.
- **💻 Interactive Console**: Integrated terminal for real-time logging and command-line control.

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- `pip install requests Pillow pystray`

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Zenith-Automator.git
   cd Zenith-Automator

### Usage
1. **Connect your account, mirroring channel and test channel**
- The user agent field should be already filled out, please dont change it unless you know what you are doing.
- Info can be found by pressing the info button on the setup screen.
- The mirroring channel is used for your message templates. To set it up, make a new server for yourself or use an existing one. Then, make a channel and name it whatever you like, but i use "message" since its simple. Lastly, right click the channel to copy the channel id. Paste that into the field. You should now be able to send messages into this channel and it will forward the latest one to whatever channel you desire, as long as you can send messages into that channel.
- The test channel is used to test messages using the test message button. It should not be a necessity to use as im confident in my program. It is not required to fill this field.
- The code is open-source. Feel free to fork it and check it in case you are warey of it. Windows may falsely flag it as malware, so please dont ask about it.
2. **Add your channels**
- There is a channel field right below the console, fill it in with your desired channel id and it will work like magic. Please note that it does require a message in your mirroring channel to actually work.
3. **Start the program**
- Click the damn start button