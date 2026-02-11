# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Define project directory for proper module resolution
project_dir = os.path.abspath(os.getcwd())

# Collect data files for faster_whisper to avoid ONNX errors
faster_whisper_datas = collect_data_files('faster_whisper')

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('app.ico', '.'),
        ('bin/ffmpeg.exe', 'bin'),  # Bundle FFmpeg binary
        ('src', 'src')  # Bundle entire src package directory
    ] + faster_whisper_datas,
    hiddenimports=[
        'pystray',
        'faster_whisper',
        'PIL',
        'ctranslate2',
        'sklearn.utils._typedefs',
        'sounddevice',
        'src',
        'src.config',
        'src.constants',
        'src.ui',
        'src.ui.main_window',
        'src.ui.about_window',
        'src.ui.welcome_window',
        'src.ui.tray',
        'src.core',
        'src.core.audio_engine',
        'src.core.transcriber',
        'src.utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],  # Remove binaries/zipfiles/datas from here for onedir mode
    exclude_binaries=True,  # CRITICAL: Set to True for onedir
    name='Synthotic_v0.4.4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    entitlements_file=None,
    icon='app.ico',
    version='version_info.txt',
)

# COLLECT creates the folder-based distribution (onedir mode)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Synthotic',  # Folder name: dist/Synthotic/
)
