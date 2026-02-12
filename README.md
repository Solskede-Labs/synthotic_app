# 🎙️ Synthotic v0.4.4

**Autonomous Meeting Recorder & Transcriber**  
Privacy-First Local Processing

[![Version](https://img.shields.io/badge/version-0.4.4-green.svg)](https://github.com/josecunha0/synthotic)
[![License](https://img.shields.io/badge/license-Custom-blue.svg)](LICENSE)

---

## 🌟 What's New in v0.4.4

### Stability & Polish

This release focuses on **stability improvements and code refinement**:

- ✅ **Enhanced audio device detection** - More reliable device enumeration with better fallback mechanisms
- ✅ **Improved error handling** - Clearer error messages for common issues
- ✅ **Code cleanup** - Removed debug logs and improved code clarity
- ✅ **Better device configuration** - Settings window with device selection persistence
- ✅ **UI improvements** - Onboarding wizard and settings enhancements

---

## 📦 Quick Start (For Users)

### Installation

1. **Windows**: Download `Synthotic_Setup.exe` from [Releases](https://github.com/josecunha0/synthotic/releases) and run the installer.
2. **Ubuntu/Linux**: Install from source (see Development Setup below).
3. Launch Synthotic.

### First Run

1. Configure a system-audio capture source:
   - **Windows**: enable `Stereo Mix` (or equivalent) in Sound Settings.
   - **Ubuntu/Linux**: use a PulseAudio/PipeWire monitor source (for example `<default_sink>.monitor`).
2. Start Synthotic
3. Click "START RECORDING"
4. Your meetings are now being captured and transcribed locally!

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Windows 10/11 or Ubuntu 22.04+
- `python3-venv` (Ubuntu/Linux)
- FFmpeg

### Installation

```bash
# Clone the repository
git clone https://github.com/josecunha0/synthotic.git
cd synthotic
```

#### Windows

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Download bundled FFmpeg binary
python utils/download_ffmpeg.py

# Run the application
python main.py
```

#### Ubuntu/Linux (venv - recommended)

```bash
# Create and activate virtual environment (PEP 668 safe)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies inside venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Install FFmpeg from apt
sudo apt update && sudo apt install -y ffmpeg

# Run the application
python main.py
```

#### Ubuntu/Linux (without activating venv)

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
sudo apt update && sudo apt install -y ffmpeg
./.venv/bin/python main.py
```

### FFmpeg setup helper

```bash
# Windows: download bundled FFmpeg
python utils/download_ffmpeg.py

# Ubuntu/Linux: install FFmpeg from apt
sudo apt update && sudo apt install -y ffmpeg
```

---

## 🏗️ Building from Source

### Step 1: Download FFmpeg

```bash
# Windows
python utils/download_ffmpeg.py

# Ubuntu/Linux
sudo apt update && sudo apt install -y ffmpeg
```

On Windows, this downloads and extracts `ffmpeg.exe` to `bin/`.  
On Ubuntu/Linux, use the system FFmpeg from your package manager.

### Step 2: Build the Application

```bash
# Install PyInstaller if needed
python -m pip install pyinstaller

# Build (creates dist/Synthotic/ folder)
pyinstaller build.spec --clean
```

**Output:** `dist/Synthotic/` - Folder with all dependencies

**Test the build:**

```bash
dist\Synthotic\Synthotic_v0.4.4.exe
```

### Step 3: Create Windows Installer (Optional)

Requires [Inno Setup 6](https://jrsoftware.org/isdl.php)

```bash
# Compile the installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

**Output:** `Output/Synthotic_Setup.exe` - Professional Windows installer (~120-150 MB)

---

## 🏛️ Architecture

### Audio Capture Flow

```
User Action → Python → FFmpeg (subprocess)
                         ↓
     DirectShow (Windows) / PulseAudio (Linux)
                         ↓
      System Audio Loopback + Microphone
                         ↓
              amix filter (real-time mixing)
                         ↓
                   WAV Output
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Audio Engine | FFmpeg subprocess | Dual-channel audio capture |
| Transcription | faster-whisper | Local AI speech-to-text |
| UI Framework | Tkinter | Cross-platform interface |
| System Tray | pystray | Background operation |
| Installer | Inno Setup | Professional deployment |

---

## 📁 Project Structure

```
Synthotic/
├── bin/                    # Optional local FFmpeg binary (Windows)
│   └── ffmpeg.exe
├── src/
│   ├── core/
│   │   ├── audio_engine.py    # FFmpeg-based recording
│   │   └── transcriber.py     # faster-whisper integration
│   ├── ui/
│   │   ├── main_window.py     # Dashboard
│   │   ├── welcome_window.py  # First-run experience
│   │   ├── about_window.py    # About dialog
│   │   └── tray.py           # System tray manager
│   ├── utils/
│   │   ├── helpers.py         # Utility functions
│   │   └── download_ffmpeg.py # FFmpeg downloader
│   ├── config.py             # User settings
│   └── constants.py          # App metadata
├── build.spec               # PyInstaller configuration
├── setup.iss               # Inno Setup installer script
├── main.py                 # Entry point
└── requirements.txt        # Python dependencies
```

---

## � Technology Stack

- **Python 3.9+** - Core language
- **FFmpeg** - Audio capture & mixing (via subprocess)
- **faster-whisper** - AI transcription (CPU-based)
- **Tkinter** - UI framework
- **pystray** - System tray integration
- **PyInstaller** - Executable bundling
- **Inno Setup** - Windows installer

---

## 🎯 Features

### Core Functionality

- ✅ Dual-channel recording (System Audio + Microphone)
- ✅ Real-time audio mixing
- ✅ Automatic transcription
- ✅ 100% local processing (no cloud)
- ✅ Background operation via system tray

### Technical Features

- ✅ Hardware-agnostic audio capture
- ✅ Automatic sample rate conversion
- ✅ Graceful error handling
- ✅ Multi-language support (English, Portuguese)
- ✅ First-run welcome experience

---

## 🐛 Troubleshooting

### "No loopback device found"

**Windows:** Enable Stereo Mix:

1. Right-click volume icon → Sounds
2. Recording tab → Right-click → Show Disabled Devices
3. Enable "Stereo Mix"

**Ubuntu/Linux:** Ensure PulseAudio/PipeWire monitor source exists:

1. Install `pavucontrol`
2. Check available sources (`pactl list short sources`)
3. Select a `*.monitor` source in Synthotic settings

### "FFmpeg not found"

**Windows:** Run the download utility:

```bash
python utils/download_ffmpeg.py
```

**Ubuntu/Linux:** Install FFmpeg:

```bash
sudo apt update && sudo apt install -y ffmpeg
```

### Application won't start (PyInstaller build)

**Check:**

1. Ensure `bin/ffmpeg.exe` is bundled in `dist/Synthotic/bin/`
2. Run from command line to see error messages:

   ```bash
   dist\Synthotic\Synthotic_v0.4.3.exe
   ```

---

## 📋 Changelog

### v0.4.4 (2026-02-10)

**Stability Improvements:**

- 🐛 Removed debug logging from production code
- 🧹 Code cleanup and refinement across all modules
- � Improved code readability and maintainability
- ⚙️ Enhanced settings persistence and device configuration

**UI Enhancements:**

- Added onboarding wizard for first-time setup
- Improved settings window with scrolling support
- Better device selection and configuration flow

---

## 👨‍💻 Developer

**José Cunha**

- LinkedIn: [josefernandocunha](https://www.linkedin.com/in/josefernandocunha/)
- GitHub: [josecunha0](https://github.com/josecunha0/)
- Website: [Synthotic.com](https://Synthotic.com)

---

## 📄 License

Copyright © 2026 José Cunha. All rights reserved.

---

## 🙏 Acknowledgments

- **FFmpeg** - The backbone of our audio capture
- **faster-whisper** - Efficient local transcription
- **Inno Setup** - Professional Windows installers

---

## 🚀 Roadmap

- [ ] Automatic meeting detection
- [ ] Speaker diarization (who said what)
- [ ] Cloud sync option (optional)
- [ ] macOS support
- [ ] Real-time transcription preview

---

**Built with ❤️ for privacy-conscious professionals**
