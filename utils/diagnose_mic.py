import json
import os
import sys

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

from src.constants import CONFIG_FILE
from src.core.audio_engine import AudioEngine


def load_config():
    if not os.path.isfile(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    print("=" * 60)
    print("SYNTHOTIC - AUDIO DIAGNOSTIC")
    print("=" * 60)

    try:
        engine = AudioEngine()
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    config = load_config()
    loopback_cfg = config.get("loopback_device_guid")
    mic_cfg = config.get("mic_device_guid")

    print(f"\nConfigured loopback: {loopback_cfg}")
    print(f"Configured microphone: {mic_cfg}\n")

    devices = engine.get_ffmpeg_devices()
    if not devices:
        print("No FFmpeg/PulseAudio devices found")
        return

    print("Available audio devices:")
    print("-" * 60)
    for i, dev in enumerate(devices, 1):
        print(f"{i}. {dev['friendly_name']}")
        print(f"   id: {dev['alternative_name']}")

    ids = {d["alternative_name"] for d in devices}

    if loopback_cfg:
        status = "OK" if loopback_cfg in ids else "MISSING"
        print(f"\nLoopback config: {status}")

    if mic_cfg:
        status = "OK" if mic_cfg in ids else "MISSING"
        print(f"Microphone config: {status}")


if __name__ == "__main__":
    main()
