import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


FFMPEG_URL_WINDOWS = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_ARCHIVE_NAME = "ffmpeg.zip"


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def download_with_progress(url: str, destination: Path) -> None:
    print(f"Downloading FFmpeg from: {url}")

    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            print(f"\rProgress: {percent:.1f}%", end="")
        else:
            print(f"\rDownloaded: {downloaded // 1024 // 1024} MB", end="")

    urllib.request.urlretrieve(url, destination, reporthook)
    print("\nDownload complete")


def extract_windows_ffmpeg(zip_path: Path, target_exe: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            if member.endswith("ffmpeg.exe") and "bin" in member:
                with zip_ref.open(member) as source, open(target_exe, "wb") as target:
                    shutil.copyfileobj(source, target)
                return
    raise FileNotFoundError("ffmpeg.exe not found in archive")


def ensure_linux_ffmpeg() -> int:
    project_root = get_project_root()
    local_bin = project_root / "bin" / "ffmpeg"
    if local_bin.is_file():
        print(f"FFmpeg already available at: {local_bin}")
        return 0

    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        print(f"FFmpeg found in PATH: {path_ffmpeg}")
        return 0

    print("FFmpeg not found on Linux.")
    print("Install it with:")
    print("  sudo apt update && sudo apt install -y ffmpeg")
    return 1


def ensure_windows_ffmpeg() -> int:
    project_root = get_project_root()
    bin_dir = project_root / "bin"
    ffmpeg_exe = bin_dir / "ffmpeg.exe"
    temp_archive = project_root / FFMPEG_ARCHIVE_NAME

    bin_dir.mkdir(exist_ok=True)

    if ffmpeg_exe.exists():
        print(f"FFmpeg already exists at: {ffmpeg_exe}")
        response = input("Re-download? (y/N): ").strip().lower()
        if response != "y":
            print("Skipping download")
            return 0
        ffmpeg_exe.unlink()

    try:
        download_with_progress(FFMPEG_URL_WINDOWS, temp_archive)
        extract_windows_ffmpeg(temp_archive, ffmpeg_exe)
    finally:
        if temp_archive.exists():
            temp_archive.unlink()

    if ffmpeg_exe.exists():
        print(f"FFmpeg ready at: {ffmpeg_exe}")
        return 0

    print("FFmpeg installation failed")
    return 1


def main() -> None:
    print("Synthotic - FFmpeg Setup")

    if is_windows():
        sys.exit(ensure_windows_ffmpeg())

    if is_linux():
        sys.exit(ensure_linux_ffmpeg())

    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        print(f"FFmpeg found in PATH: {path_ffmpeg}")
        sys.exit(0)

    print("Unsupported platform and FFmpeg not found in PATH")
    sys.exit(1)


if __name__ == "__main__":
    main()
