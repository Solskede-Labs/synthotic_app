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

1. Download `Synthotic_Setup.exe` from [Releases](https://github.com/josecunha0/synthotic/releases)
2. Run the installer
3. Launch from Start Menu or Desktop
4. Done! No configuration needed.

### First Run

1. Enable "Stereo Mix" in Windows Sound Settings:
   - Right-click volume icon → Sounds → Recording tab
   - Right-click empty space → Show Disabled Devices
   - Enable "Stereo Mix"
2. Start Synthotic
3. Click "START RECORDING"
4. Your meetings are now being captured and transcribed locally!

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Windows 10/11
- FFmpeg (auto-downloaded by our utility)

### Installation

```bash
# Clone the repository
git clone https://github.com/josecunha0/synthotic.git
cd synthotic

# Install dependencies
pip install -r requirements.txt

# Download FFmpeg (required for audio capture)
python utils/download_ffmpeg.py

# Run the application
python main.py
```

---

## 🏗️ Building from Source

### Step 1: Download FFmpeg

```bash
python utils/download_ffmpeg.py
```

This downloads the official FFmpeg Windows build and extracts `ffmpeg.exe` to the `bin/` folder.

### Step 2: Build the Application

```bash
# Install PyInstaller if needed
pip install pyinstaller

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
              DirectShow Capture
                         ↓
         System Audio (Stereo Mix) + Microphone
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
├── bin/                    # FFmpeg binary (auto-downloaded)
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

**Solution:** Enable Stereo Mix in Windows:
1. Right-click volume icon → Sounds
2. Recording tab → Right-click → Show Disabled Devices
3. Enable "Stereo Mix"

### "FFmpeg not found"

**Solution:** Run the download utility:
```bash
python utils/download_ffmpeg.py
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
- [ ] macOS and Linux support
- [ ] Real-time transcription preview

---

**Built with ❤️ for privacy-conscious professionals**
