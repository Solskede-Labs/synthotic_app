# Synthotic Audio Engine
# GitHub: https://github.com/josecunha0/synthotic

import os
import sys
import subprocess
import datetime
import logging
import json
import time
import re
import sounddevice as sd
from typing import Optional, Tuple

from src.constants import BASE_DIR, SAMPLE_RATE

logger = logging.getLogger(__name__)


class LoopbackNotFoundError(Exception):
    pass


class FFmpegRuntimeError(Exception):
    pass


class AudioEngine:
    
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self.wav_path: Optional[str] = None
        self._ffmpeg_path = self._find_ffmpeg()
        
        if not self._ffmpeg_path:
            raise RuntimeError(
                "FFmpeg not found. Please run 'python utils/download_ffmpeg.py' "
                "to download the required binary."
            )
        
        logger.info(f"FFmpeg found at: {self._ffmpeg_path}")
    
    def _find_ffmpeg(self) -> Optional[str]:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dev_path = os.path.join(script_dir, "bin", "ffmpeg.exe")
        
        if os.path.isfile(dev_path):
            return dev_path
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            frozen_path = os.path.join(sys._MEIPASS, "bin", "ffmpeg.exe")
            if os.path.isfile(frozen_path):
                return frozen_path
        
        return None
    
    def get_ffmpeg_devices(self):
        cmd = [self._ffmpeg_path, "-f", "dshow", "-list_devices", "true", "-i", "dummy"]
        devices = []
        
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
            
            lines = res.stderr.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if '"' in line and ('(audio)' in line or '(video)' in line or '(video, audio)' in line):
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        friendly_name = match_name.group(1)
                        
                        if '(audio)' in line:
                            device_type = "audio"
                        elif '(video)' in line:
                            device_type = "video"
                        else:
                            device_type = "video_audio"
                        
                        alternative_name = None
                        if i + 1 < len(lines) and "Alternative name" in lines[i + 1]:
                            match_alt = re.search(r'Alternative name "(.*)"', lines[i + 1])
                            if match_alt:
                                alternative_name = match_alt.group(1)
                        
                        devices.append({
                            "friendly_name": friendly_name,
                            "alternative_name": alternative_name or friendly_name,
                            "type": device_type
                        })
                
                i += 1
            
            return devices
            
        except Exception as e:
            logger.error(f"Error enumerating FFmpeg devices: {e}")
            return []
    
    def _load_device_guids_from_config(self):
        try:
            from src.constants import CONFIG_FILE
            
            if os.path.isfile(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    loopback_guid = config.get('loopback_device_guid')
                    mic_guid = config.get('mic_device_guid')
                    
                    if loopback_guid or mic_guid:
                        logger.info(f"Loaded device GUIDs from config")
                    
                    return loopback_guid, mic_guid
        except Exception as e:
            pass
        
        return None, None
    
    def _discover_devices(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            loopback_guid, mic_guid = self._load_device_guids_from_config()
            if loopback_guid:
                logger.info(f"Using configured device GUIDs from settings")
                return loopback_guid, mic_guid
            
            devices = sd.query_devices()
            loopback_device = None
            mic_device = None
            fallback_mix_device = None
            
            loopback_keywords = [
                'stereo mix', 'loopback', 'wave out mix', 'what u hear', 'what you hear',
                'mixagem estéreo', 'mixagem estereo', 'mixagem',
                'mezcla estéreo', 'mezcla estereo', 'mezcla'
            ]
            
            for device in devices:
                device_name = device['name']
                device_lower = device_name.lower()
                input_channels = device['max_input_channels']
                
                if any(keyword in device_lower for keyword in loopback_keywords):
                    loopback_device = device_name
                    logger.info(f"Found loopback device: {device_name}")
                    continue
                
                if input_channels == 0:
                    continue
                
                if 'mix' in device_lower and fallback_mix_device is None:
                    fallback_mix_device = device_name
                
                if any(keyword in device_lower for keyword in ['microphone', 'mic', 'input']) \
                   and not any(keyword in device_lower for keyword in loopback_keywords):
                    if mic_device is None:
                        mic_device = device_name
                        logger.info(f"Found microphone device: {device_name}")
            
            if not loopback_device:
                if fallback_mix_device:
                    loopback_device = fallback_mix_device
                    logger.warning(f"No exact loopback match, using fallback: {fallback_mix_device}")
                else:
                    logger.warning("No loopback device found")
            
            if not mic_device:
                logger.warning("No microphone device found")
            
            return loopback_device, mic_device
        
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return None, None
    
    def _resolve_device_name(self, friendly_name: str) -> str:
        if not friendly_name:
            return friendly_name
            
        cmd = [self._ffmpeg_path, "-f", "dshow", "-list_devices", "true", "-i", "dummy"]
        
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
            output = res.stderr
            lines = output.split('\n')
            
            # Exact match
            for i, line in enumerate(lines):
                if f'"{friendly_name}"' in line and ('(audio)' in line or '(video, audio)' in line):
                    if i + 1 < len(lines) and "Alternative name" in lines[i+1]:
                        match = re.search(r'Alternative name "(.*)"', lines[i+1])
                        if match:
                            alt_name = match.group(1)
                            logger.info(f"Resolved device to GUID")
                            return alt_name
            
            # Fuzzy match - first 20 chars
            friendly_prefix = friendly_name[:20].lower()
            
            for i, line in enumerate(lines):
                if '"' in line and ('(audio)' in line or '(video, audio)' in line):
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        ffmpeg_device_name = match_name.group(1)
                        ffmpeg_prefix = ffmpeg_device_name[:20].lower()
                        
                        if friendly_prefix == ffmpeg_prefix:
                            if i + 1 < len(lines) and "Alternative name" in lines[i+1]:
                                match_alt = re.search(r'Alternative name "(.*)"', lines[i+1])
                                if match_alt:
                                    alt_name = match_alt.group(1)
                                    logger.info(f"Resolved device to GUID (fuzzy match)")
                                    return alt_name
            
            # Substring match
            for i, line in enumerate(lines):
                if ('(audio)' in line or '(video, audio)' in line):
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        ffmpeg_device_name = match_name.group(1)
                        if friendly_name.lower() in ffmpeg_device_name.lower():
                            if i + 1 < len(lines) and "Alternative name" in lines[i+1]:
                                match_alt = re.search(r'Alternative name "(.*)"', lines[i+1])
                                if match_alt:
                                    alt_name = match_alt.group(1)
                                    logger.info(f"Resolved device to GUID (substring match)")
                                    return alt_name
            
            logger.warning(f"Could not resolve GUID for device, using original name")
            return friendly_name
            
        except Exception as e:
            logger.error(f"Error parsing FFmpeg device list: {e}")
            return friendly_name

    def start(self) -> str:
        from src.constants import CONFIG_FILE
        output_base = BASE_DIR
        try:
            if os.path.isfile(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configured_folder = config.get('output_folder')
                    if configured_folder:
                        output_base = configured_folder
                        logger.info(f"Using configured output folder: {output_base}")
        except Exception:
            pass
        
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = os.path.join(output_base, f"Live_{ts}")
        os.makedirs(folder, exist_ok=True)
        self.wav_path = os.path.join(folder, "audio.wav")
        
        loopback, mic = self._discover_devices()
        
        if not loopback:
            raise LoopbackNotFoundError()
            
        if loopback and loopback.startswith('@device_cm_'):
            loopback_arg = loopback
        else:
            loopback_arg = self._resolve_device_name(loopback)
        
        if mic:
            if mic.startswith('@device_cm_'):
                mic_arg = mic
            else:
                mic_arg = self._resolve_device_name(mic)
        else:
            mic_arg = None
        
        
        cmd = [self._ffmpeg_path]
        
        if mic:
            logger.info(f"Starting dual-channel recording: {loopback} + {mic}")
            logger.debug(f"  → Loopback GUID/Name: {loopback_arg}")
            logger.debug(f"  → Mic GUID/Name: {mic_arg}")
            
            cmd.extend([
                "-f", "dshow",
                "-i", f"audio={loopback_arg}",
                "-f", "dshow",
                "-i", f"audio={mic_arg}",
                # Use amerge + pan for better audio mixing control
                # This ensures both inputs are heard at balanced levels
                "-filter_complex",
                "[0:a]volume=0.9[a0];[1:a]volume=1.2[a1];[a0][a1]amerge=inputs=2[merged];[merged]pan=stereo|c0<c0+c2|c1<c1+c3[out]",
                "-map", "[out]",
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])
        else:
            logger.info(f"Starting recording without microphone")
            cmd.extend([
                "-f", "dshow",
                "-i", f"audio={loopback_arg}",
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])
        
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            logger.info(f"FFmpeg process started (PID: {self._process.pid})")
            logger.info(f"Recording to: {self.wav_path}")
            
            time.sleep(0.5)
            if self._process.poll() is not None:
                _, stderr_output = self._process.communicate()
                error_msg = stderr_output.decode('utf-8', errors='replace') if stderr_output else "Unknown error"
                logger.error(f"FFmpeg process died immediately. Exit code: {self._process.returncode}")
                logger.error(f"FFmpeg stderr: {error_msg}")
                raise FFmpegRuntimeError(
                    f"FFmpeg failed to start recording. Check the log file for details."
                )
            
        except FFmpegRuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to start FFmpeg process: {e}")
            raise FFmpegRuntimeError(str(e))
        
        return self.wav_path
    
    def stop(self) -> str:
        if self._process and self._process.poll() is None:
            try:
                self._process.communicate(input=b'q', timeout=5)
                logger.info("FFmpeg process stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg did not stop gracefully, terminating...")
                self._process.terminate()
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    logger.error("FFmpeg process killed forcefully")
            except Exception as e:
                logger.error(f"Error stopping FFmpeg: {e}")
                self._process.kill()
        
        if not self.wav_path or not os.path.exists(self.wav_path):
            raise FFmpegRuntimeError(
                f"Recording failed: Output file does not exist."
            )
        
        file_size = os.path.getsize(self.wav_path)
        if file_size == 0:
            raise FFmpegRuntimeError(
                f"Recording failed: Output file is empty."
            )
        
        logger.info(f"Recording stopped successfully. File size: {file_size} bytes")
        return self.wav_path
