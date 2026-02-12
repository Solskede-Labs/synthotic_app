import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def create_no_window_flags() -> int:
    if is_windows() and hasattr(subprocess, "CREATE_NO_WINDOW"):
        return subprocess.CREATE_NO_WINDOW
    return 0


def default_recordings_dir() -> str:
    home = os.path.expanduser("~")
    docs = os.path.join(home, "Documents")
    if os.path.isdir(docs):
        return os.path.join(docs, "Synthotic_Recordings")
    return os.path.join(home, "Synthotic_Recordings")


def find_ffmpeg_binary() -> Optional[str]:
    root_dir = Path(__file__).resolve().parents[1]
    bin_dir = root_dir / "bin"

    candidates = []
    if is_windows():
        candidates.append(bin_dir / "ffmpeg.exe")
    else:
        candidates.append(bin_dir / "ffmpeg")

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        frozen_bin = Path(sys._MEIPASS) / "bin"
        if is_windows():
            candidates.append(frozen_bin / "ffmpeg.exe")
        else:
            candidates.append(frozen_bin / "ffmpeg")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    if is_windows():
        which = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    else:
        which = shutil.which("ffmpeg")

    return which


def open_path(path: str) -> bool:
    try:
        if is_windows() and hasattr(os, "startfile"):
            os.startfile(path)
            return True

        if is_linux():
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True

        if sys.platform == "darwin":
            subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True

        return False
    except Exception:
        return False


def open_audio_settings() -> bool:
    if is_windows():
        try:
            subprocess.run(
                "control mmsys.cpl,,1",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=create_no_window_flags()
            )
            return True
        except Exception:
            return False

    if is_linux():
        candidates = [
            ["pavucontrol"],
            ["gnome-control-center", "sound"],
            ["plasma-systemsettings", "kcm_pulseaudio"],
            ["mate-volume-control"],
            ["xfce4-settings-manager"]
        ]
        for cmd in candidates:
            if shutil.which(cmd[0]):
                try:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except Exception:
                    continue

    return False
