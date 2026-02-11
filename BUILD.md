# 🚀 Quick Build Guide - Synthotic v0.4.4

## For Users (End-to-End Installation)

### Option 1: Use the Installer (Recommended)

1. Download `Synthotic_Setup.exe`
2. Run the installer
3. Done!

### Option 2: Build from Source

```bash
# 1. Download FFmpeg
python utils/download_ffmpeg.py

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build
pyinstaller build.spec --clean

# 4. Create installer (requires Inno Setup)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

# 5. Distribute
# Share: Output\Synthotic_Setup.exe
```

---

## For Developers (Quick Test)

```bash
# First time setup
python utils/download_ffmpeg.py
pip install -r requirements.txt

# Run in development mode
python main.py

# Build executable
pyinstaller build.spec --clean
dist\Synthotic\Synthotic_v1.1.3.exe
```

---

## Critical Files

| File | Purpose | Required For |
|------|---------|-------------|
| `bin/ffmpeg.exe` | Audio capture | Development + Production |
| `build.spec` | PyInstaller config | Building EXE |
| `setup.iss` | Inno Setup config | Creating installer |
| `app.ico` | Application icon | Branding |
| `version_info.txt` | EXE metadata | Version info |

---

## Dependencies

### Runtime (Bundled in EXE):
- FFmpeg (in `bin/`)
- faster-whisper models (downloaded on first run)
- Python runtime (via PyInstaller)

### Development Only:
```
pystray
Pillow
faster-whisper
```

**Removed in v0.4.4:**
- ~~pyaudiowpatch~~
- ~~soundfile~~
- ~~numpy~~

---

## Build Outputs

### PyInstaller (onedir):
```
dist/
└── Synthotic/
    ├── Synthotic_v0.4.4.exe  (main executable)
    ├── bin/
    │   └── ffmpeg.exe       (audio engine)
    └── _internal/           (dependencies)
```

### Inno Setup:
```
Output/
└── Synthotic_Setup.exe  (installer, ~120-150 MB)
```

---

## Testing Workflow

### 1. FFmpeg Test
```bash
python -c "from src.core.audio_engine import AudioEngine; e = AudioEngine(); print(e._discover_devices())"
```
**Expected:** `('Stereo Mix', 'Microphone')` or similar

### 2. Application Test
```bash
python main.py
# → Click "START RECORDING"
# → Play audio + speak into mic
# → Click "STOP RECORDING"
# → Check ~/Documents/Synthotic_Recordings/
```

### 3. Build Test
```bash
pyinstaller build.spec --clean
dist\Synthotic\Synthotic_v0.4.4.exe
# Should launch instantly (no 5-10s delay)
```

### 4. Installer Test
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
Output\Synthotic_Setup.exe
# Install → Test → Uninstall
```

---

## Common Issues

### ❌ "FFmpeg not found"
```bash
python utils/download_ffmpeg.py
```

### ❌ "No loopback device found"
Enable Stereo Mix in Windows Sound Settings

### ❌ "Build failed - missing data files"
Ensure `bin/ffmpeg.exe` exists before building

### ❌ "Installer missing files"
Build with PyInstaller first: `pyinstaller build.spec --clean`

---

## Version Update Checklist

When releasing a new version:

- [ ] Update `src/constants.py` → `VERSION`, `BUILD_DATE`
- [ ] Update `version_info.txt` → all version fields
- [ ] Update `build.spec` → `name` field
- [ ] Update `setup.iss` → `MyAppVersion`
- [ ] Update `README.md` → version badge
- [ ] Build and test
- [ ] Tag Git release: `git tag v0.4.4`

---

## Distribution

### GitHub Release:
1. Build installer: `Synthotic_Setup.exe`
2. Create GitHub release: `v0.4.4`
3. Upload `Synthotic_Setup.exe` as asset
4. Update release notes

### Direct Distribution:
Share `Output\Synthotic_Setup.exe` (~350-360 MB)

---

**Build Time:** ~2-5 minutes  
**Installer Size:** ~350-360 MB  
**Startup Time:** <1 second (onedir mode)
