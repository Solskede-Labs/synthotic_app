"""
Synthotic - Microphone Diagnostic Script
Tests FFmpeg device access and validates GUIDs from config
"""

import os
import sys
import json
import subprocess
import re

# Setup paths
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

from src.constants import BASE_DIR, CONFIG_FILE

def find_ffmpeg():
    """Locate FFmpeg binary"""
    dev_path = os.path.join(script_dir, "bin", "ffmpeg.exe")
    if os.path.isfile(dev_path):
        return dev_path
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        frozen_path = os.path.join(sys._MEIPASS, "bin", "ffmpeg.exe")
        if os.path.isfile(frozen_path):
            return frozen_path
    
    return None

def list_ffmpeg_devices(ffmpeg_path):
    """Get all FFmpeg DirectShow devices"""
    cmd = [ffmpeg_path, "-f", "dshow", "-list_devices", "true", "-i", "dummy"]
    
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        devices = []
        lines = res.stderr.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if '"' in line and ('(audio)' in line or '(video, audio)' in line):
                match_name = re.search(r'"([^"]+)"', line)
                if match_name:
                    friendly_name = match_name.group(1)
                    device_type = "audio" if "(audio)" in line else "video_audio"
                    
                    alternative_name = None
                    if i + 1 < len(lines) and "Alternative name" in lines[i + 1]:
                        match_alt = re.search(r'Alternative name "(.*)"', lines[i + 1])
                        if match_alt:
                            alternative_name = match_alt.group(1)
                    
                    devices.append({
                        "friendly_name": friendly_name,
                        "alternative_name": alternative_name or "(None)",
                        "type": device_type
                    })
            
            i += 1
        
        return devices
        
    except Exception as e:
        print(f"[ERROR] Failed to enumerate devices: {e}")
        return []

def load_config():
    """Load config.json"""
    if not os.path.isfile(CONFIG_FILE):
        return None
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=" * 60)
    print("SYNTHOTIC - MICROPHONE DIAGNOSTIC")
    print("=" * 60)
    
    # Find FFmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("[ERROR] FFmpeg not found!")
        return
    
    print(f"\n[OK] FFmpeg found: {ffmpeg_path}\n")
    
    # Load config
    config = load_config()
    if not config:
        print("[WARNING] No config.json found\n")
        loopback_guid_config = None
        mic_guid_config = None
    else:
        loopback_guid_config = config.get('loopback_device_guid')
        mic_guid_config = config.get('mic_device_guid')
        
        print("CONFIG DEVICES:")
        print(f"  Loopback GUID: {loopback_guid_config}")
        print(f"  Mic GUID: {mic_guid_config}\n")
    
    # List all FFmpeg devices
    print("AVAILABLE FFMPEG DEVICES:")
    print("-" * 60)
    devices = list_ffmpeg_devices(ffmpeg_path)
    
    for idx, dev in enumerate(devices, 1):
        print(f"{idx}. {dev['friendly_name']}")
        print(f"   Type: {dev['type']}")
        print(f"   GUID: {dev['alternative_name']}")
        print()
    
    # Validate GUIDs
    print("=" * 60)
    print("VALIDATION:")
    print("-" * 60)
    
    if loopback_guid_config:
        found = any(d['alternative_name'] == loopback_guid_config for d in devices)
        status = "[OK]" if found else "[FAIL]"
        print(f"{status} Loopback GUID from config {'FOUND' if found else 'NOT FOUND'} in FFmpeg devices")
    
    if mic_guid_config:
        found = any(d['alternative_name'] == mic_guid_config for d in devices)
        status = "[OK]" if found else "[FAIL]"
        print(f"{status} Mic GUID from config {'FOUND' if found else 'NOT FOUND'} in FFmpeg devices")
        
        if not found:
            print("\n[WARNING] Microphone GUID is INVALID!")
            print("  → The device might have been disabled, unplugged, or changed")
            print("  → Open Settings and select the correct microphone again")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
