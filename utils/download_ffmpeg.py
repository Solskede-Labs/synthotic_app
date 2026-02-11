"""
FFmpeg Download Utility for Synthotic.

This script automatically downloads the FFmpeg Windows build and extracts
the ffmpeg.exe binary to the bin/ folder. This eliminates the need for
manual FFmpeg installation.

Usage:
    python utils/download_ffmpeg.py
"""
import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


# FFmpeg build URLs (using official gyan.dev builds)
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_FILENAME = "ffmpeg.zip"


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path object pointing to the project root.
    """
    # Script is in utils/, so parent is project root
    return Path(__file__).parent.parent


def download_with_progress(url: str, destination: Path) -> None:
    """
    Download a file with progress indication.
    
    Args:
        url: URL to download from.
        destination: Local path to save the file.
    """
    print(f"Downloading FFmpeg from: {url}")
    print("This may take a few minutes depending on your connection...")
    
    def reporthook(block_num, block_size, total_size):
        """Display download progress."""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB)", end='')
        else:
            print(f"\rDownloaded: {downloaded // 1024 // 1024}MB", end='')
    
    try:
        urllib.request.urlretrieve(url, destination, reporthook)
        print("\n✓ Download complete!")
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        raise


def extract_ffmpeg(zip_path: Path, bin_dir: Path) -> None:
    """
    Extract ffmpeg.exe from the downloaded ZIP archive.
    
    Args:
        zip_path: Path to the downloaded ZIP file.
        bin_dir: Destination directory for ffmpeg.exe.
    """
    print("\nExtracting FFmpeg binary...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find ffmpeg.exe in the archive (it's usually in a subfolder)
            ffmpeg_found = False
            
            for member in zip_ref.namelist():
                if member.endswith('ffmpeg.exe') and 'bin' in member:
                    # Extract to bin/ directory
                    source = zip_ref.open(member)
                    target = bin_dir / "ffmpeg.exe"
                    
                    with open(target, 'wb') as f:
                        shutil.copyfileobj(source, f)
                    
                    ffmpeg_found = True
                    print(f"✓ Extracted: {target}")
                    break
            
            if not ffmpeg_found:
                raise FileNotFoundError("ffmpeg.exe not found in the archive")
    
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        raise


def main():
    """Main execution function."""
    print("=" * 60)
    print("Synthotic - FFmpeg Download Utility")
    print("=" * 60)
    
    # Get paths
    project_root = get_project_root()
    bin_dir = project_root / "bin"
    ffmpeg_path = bin_dir / "ffmpeg.exe"
    temp_zip = project_root / FFMPEG_FILENAME
    
    # Check if FFmpeg already exists
    if ffmpeg_path.exists():
        print(f"\n✓ FFmpeg already exists at: {ffmpeg_path}")
        response = input("Do you want to re-download? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping download.")
            return
        else:
            print("Removing existing FFmpeg...")
            ffmpeg_path.unlink()
    
    # Create bin/ directory if it doesn't exist
    bin_dir.mkdir(exist_ok=True)
    print(f"\n✓ Binary directory ready: {bin_dir}")
    
    try:
        # Download FFmpeg
        download_with_progress(FFMPEG_URL, temp_zip)
        
        # Extract FFmpeg
        extract_ffmpeg(temp_zip, bin_dir)
        
        # Cleanup temporary ZIP file
        print("\nCleaning up temporary files...")
        temp_zip.unlink()
        print("✓ Cleanup complete!")
        
        # Verify installation
        if ffmpeg_path.exists():
            size_mb = ffmpeg_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("✓ SUCCESS! FFmpeg is ready to use.")
            print(f"  Location: {ffmpeg_path}")
            print(f"  Size: {size_mb:.1f} MB")
            print("=" * 60)
            print("\nYou can now run Synthotic with FFmpeg audio capture enabled.")
        else:
            raise FileNotFoundError("FFmpeg binary was not created successfully")
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ ERROR: {e}")
        print("=" * 60)
        print("\nManual installation instructions:")
        print("1. Download FFmpeg from: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("2. Extract ffmpeg.exe to the bin/ folder in the project root")
        sys.exit(1)


if __name__ == "__main__":
    main()
