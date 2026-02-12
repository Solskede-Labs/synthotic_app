import datetime
import json
import logging
import os
import re
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import sounddevice as sd

from src.constants import BASE_DIR, SAMPLE_RATE
from src.platform_utils import create_no_window_flags, find_ffmpeg_binary, is_linux, is_windows

logger = logging.getLogger(__name__)


class LoopbackNotFoundError(Exception):
    pass


class FFmpegRuntimeError(Exception):
    pass


class AudioEngine:

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self.wav_path: Optional[str] = None
        self._ffmpeg_path = find_ffmpeg_binary()

        if not self._ffmpeg_path:
            if is_linux():
                raise RuntimeError("FFmpeg not found. Install FFmpeg with: sudo apt install ffmpeg")
            raise RuntimeError(
                "FFmpeg not found. Please run 'python utils/download_ffmpeg.py' to download the required binary."
            )

        logger.info(f"FFmpeg found at: {self._ffmpeg_path}")

    def _run_capture(self, cmd: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=create_no_window_flags()
        )

    def _list_windows_ffmpeg_devices(self) -> List[Dict[str, str]]:
        cmd = [self._ffmpeg_path, "-f", "dshow", "-list_devices", "true", "-i", "dummy"]
        devices: List[Dict[str, str]] = []

        try:
            res = self._run_capture(cmd)
            lines = res.stderr.split("\n")
            i = 0

            while i < len(lines):
                line = lines[i]

                if '"' in line and ("(audio)" in line or "(video)" in line or "(video, audio)" in line):
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        friendly_name = match_name.group(1)

                        if "(audio)" in line:
                            device_type = "audio"
                        elif "(video)" in line:
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

    def _get_pulse_source_descriptions(self) -> Dict[str, str]:
        descriptions: Dict[str, str] = {}
        try:
            res = self._run_capture(["pactl", "list", "sources"])
            current_name = None

            for line in res.stdout.splitlines():
                name_match = re.match(r"\s*Name:\s*(.+)$", line)
                if name_match:
                    current_name = name_match.group(1).strip()
                    continue

                desc_match = re.match(r"\s*Description:\s*(.+)$", line)
                if desc_match and current_name:
                    descriptions[current_name] = desc_match.group(1).strip()

        except Exception:
            return {}

        return descriptions

    def _list_linux_pulse_devices(self) -> List[Dict[str, str]]:
        devices: List[Dict[str, str]] = []
        try:
            res = self._run_capture(["pactl", "list", "short", "sources"])
            descriptions = self._get_pulse_source_descriptions()

            for raw_line in res.stdout.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                source_name = parts[1].strip()
                if not source_name:
                    continue

                source_desc = descriptions.get(source_name)
                if source_desc and source_desc != source_name:
                    friendly_name = f"{source_desc} [{source_name}]"
                else:
                    friendly_name = source_name

                devices.append({
                    "friendly_name": friendly_name,
                    "alternative_name": source_name,
                    "type": "audio"
                })
        except Exception:
            return []

        return devices

    def _list_linux_ffmpeg_devices(self) -> List[Dict[str, str]]:
        devices: List[Dict[str, str]] = []
        try:
            res = self._run_capture([self._ffmpeg_path, "-sources", "pulse"])
            output = f"{res.stdout}\n{res.stderr}"
            found = set()

            for line in output.splitlines():
                match = re.search(r"\*\s+([A-Za-z0-9_:@.\-]+)", line)
                if not match:
                    continue
                source_name = match.group(1).strip()
                if not source_name or source_name in found:
                    continue
                found.add(source_name)
                devices.append({
                    "friendly_name": source_name,
                    "alternative_name": source_name,
                    "type": "audio"
                })
        except Exception:
            return []

        return devices

    def get_ffmpeg_devices(self) -> List[Dict[str, str]]:
        if is_windows():
            return self._list_windows_ffmpeg_devices()
        if is_linux():
            devices = self._list_linux_pulse_devices()
            if devices:
                return devices
            return self._list_linux_ffmpeg_devices()
        return []

    def _load_device_guids_from_config(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            from src.constants import CONFIG_FILE

            if os.path.isfile(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    loopback_guid = config.get("loopback_device_guid")
                    mic_guid = config.get("mic_device_guid")

                    if loopback_guid or mic_guid:
                        logger.info("Loaded configured audio devices from config")

                    return loopback_guid, mic_guid
        except Exception:
            pass

        return None, None

    def _discover_windows_devices(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            devices = sd.query_devices()
            loopback_device = None
            mic_device = None
            fallback_mix_device = None

            loopback_keywords = [
                "stereo mix", "loopback", "wave out mix", "what u hear", "what you hear",
                "mixagem estereo", "mixagem", "mezcla estereo", "mezcla"
            ]

            for device in devices:
                device_name = device["name"]
                device_lower = device_name.lower()
                input_channels = device["max_input_channels"]

                if any(keyword in device_lower for keyword in loopback_keywords):
                    loopback_device = device_name
                    logger.info(f"Found loopback device: {device_name}")
                    continue

                if input_channels == 0:
                    continue

                if "mix" in device_lower and fallback_mix_device is None:
                    fallback_mix_device = device_name

                if any(keyword in device_lower for keyword in ["microphone", "mic", "input"]):
                    if not any(keyword in device_lower for keyword in loopback_keywords) and mic_device is None:
                        mic_device = device_name
                        logger.info(f"Found microphone device: {device_name}")

            if not loopback_device and fallback_mix_device:
                loopback_device = fallback_mix_device
                logger.warning(f"No exact loopback match, using fallback: {fallback_mix_device}")

            if not loopback_device:
                logger.warning("No loopback device found")

            if not mic_device:
                logger.warning("No microphone device found")

            return loopback_device, mic_device

        except Exception as e:
            logger.error(f"Error discovering Windows devices: {e}")
            return None, None

    def _get_pulse_default_source(self) -> Optional[str]:
        try:
            res = self._run_capture(["pactl", "get-default-source"])
            source = res.stdout.strip()
            if source:
                return source
        except Exception:
            pass

        try:
            res = self._run_capture(["pactl", "info"])
            for line in res.stdout.splitlines():
                if line.lower().startswith("default source"):
                    return line.split(":", 1)[1].strip()
        except Exception:
            pass

        return None

    def _get_pulse_default_monitor(self) -> Optional[str]:
        sink_name = None
        try:
            res = self._run_capture(["pactl", "get-default-sink"])
            sink_name = res.stdout.strip() or None
        except Exception:
            sink_name = None

        if sink_name is None:
            try:
                res = self._run_capture(["pactl", "info"])
                for line in res.stdout.splitlines():
                    if line.lower().startswith("default sink"):
                        sink_name = line.split(":", 1)[1].strip()
                        break
            except Exception:
                sink_name = None

        if not sink_name:
            return None

        if sink_name.endswith(".monitor"):
            return sink_name

        return f"{sink_name}.monitor"

    def _discover_linux_devices(self) -> Tuple[Optional[str], Optional[str]]:
        devices = self.get_ffmpeg_devices()
        device_names = [d["alternative_name"] for d in devices if d.get("type") == "audio"]

        if not device_names:
            logger.warning("No PulseAudio/PipeWire sources found")
            return None, None

        default_source = self._get_pulse_default_source()
        default_monitor = self._get_pulse_default_monitor()

        loopback_candidates = [
            name for name in device_names
            if name.endswith(".monitor") or "monitor" in name.lower()
        ]
        mic_candidates = [name for name in device_names if name not in loopback_candidates]

        loopback_device = None
        mic_device = None

        if default_monitor and default_monitor in device_names:
            loopback_device = default_monitor
        elif loopback_candidates:
            loopback_device = loopback_candidates[0]
        elif "default" in device_names:
            loopback_device = "default"

        if default_source and default_source in device_names and default_source != loopback_device:
            mic_device = default_source
        else:
            for candidate in mic_candidates:
                if candidate != loopback_device:
                    mic_device = candidate
                    break

        if not mic_device and "default" in device_names and loopback_device != "default":
            mic_device = "default"

        if loopback_device:
            logger.info(f"Selected Linux loopback source: {loopback_device}")
        else:
            logger.warning("No Linux loopback monitor source found")

        if mic_device:
            logger.info(f"Selected Linux microphone source: {mic_device}")
        else:
            logger.warning("No Linux microphone source found")

        return loopback_device, mic_device

    def _discover_devices(self) -> Tuple[Optional[str], Optional[str]]:
        loopback_guid, mic_guid = self._load_device_guids_from_config()
        if loopback_guid:
            return loopback_guid, mic_guid

        if is_windows():
            return self._discover_windows_devices()

        if is_linux():
            return self._discover_linux_devices()

        return None, None

    def _resolve_windows_device_name(self, friendly_name: str) -> str:
        if not friendly_name:
            return friendly_name

        cmd = [self._ffmpeg_path, "-f", "dshow", "-list_devices", "true", "-i", "dummy"]

        try:
            res = self._run_capture(cmd)
            lines = res.stderr.split("\n")

            for i, line in enumerate(lines):
                if f'"{friendly_name}"' in line and ("(audio)" in line or "(video, audio)" in line):
                    if i + 1 < len(lines) and "Alternative name" in lines[i + 1]:
                        match = re.search(r'Alternative name "(.*)"', lines[i + 1])
                        if match:
                            return match.group(1)

            friendly_prefix = friendly_name[:20].lower()

            for i, line in enumerate(lines):
                if '"' in line and ("(audio)" in line or "(video, audio)" in line):
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        ffmpeg_device_name = match_name.group(1)
                        ffmpeg_prefix = ffmpeg_device_name[:20].lower()

                        if friendly_prefix == ffmpeg_prefix and i + 1 < len(lines) and "Alternative name" in lines[i + 1]:
                            match_alt = re.search(r'Alternative name "(.*)"', lines[i + 1])
                            if match_alt:
                                return match_alt.group(1)

            for i, line in enumerate(lines):
                if "(audio)" in line or "(video, audio)" in line:
                    match_name = re.search(r'"([^"]+)"', line)
                    if match_name:
                        ffmpeg_device_name = match_name.group(1)
                        if friendly_name.lower() in ffmpeg_device_name.lower():
                            if i + 1 < len(lines) and "Alternative name" in lines[i + 1]:
                                match_alt = re.search(r'Alternative name "(.*)"', lines[i + 1])
                                if match_alt:
                                    return match_alt.group(1)

            return friendly_name

        except Exception as e:
            logger.error(f"Error resolving Windows device name: {e}")
            return friendly_name

    def _build_windows_command(self, loopback_arg: str, mic_arg: Optional[str]) -> List[str]:
        cmd = [self._ffmpeg_path]

        if mic_arg:
            cmd.extend([
                "-f", "dshow",
                "-i", f"audio={loopback_arg}",
                "-f", "dshow",
                "-i", f"audio={mic_arg}",
                "-filter_complex",
                "[0:a]volume=0.9[a0];[1:a]volume=1.2[a1];[a0][a1]amerge=inputs=2[merged];[merged]pan=stereo|c0<c0+c2|c1<c1+c3[out]",
                "-map", "[out]",
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])
        else:
            cmd.extend([
                "-f", "dshow",
                "-i", f"audio={loopback_arg}",
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])

        return cmd

    def _build_linux_command(self, loopback_arg: str, mic_arg: Optional[str]) -> List[str]:
        cmd = [self._ffmpeg_path]

        if mic_arg:
            cmd.extend([
                "-f", "pulse",
                "-i", loopback_arg,
                "-f", "pulse",
                "-i", mic_arg,
                "-filter_complex",
                "[0:a]volume=0.9[a0];[1:a]volume=1.2[a1];[a0][a1]amix=inputs=2:duration=longest:normalize=0[out]",
                "-map", "[out]",
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])
        else:
            cmd.extend([
                "-f", "pulse",
                "-i", loopback_arg,
                "-ar", str(SAMPLE_RATE),
                "-ac", "2",
                "-y",
                self.wav_path
            ])

        return cmd

    def start(self) -> str:
        from src.constants import CONFIG_FILE

        output_base = BASE_DIR
        try:
            if os.path.isfile(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    configured_folder = config.get("output_folder")
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

        if is_windows():
            if loopback.startswith("@device_cm_"):
                loopback_arg = loopback
            else:
                loopback_arg = self._resolve_windows_device_name(loopback)

            if mic:
                if mic.startswith("@device_cm_"):
                    mic_arg = mic
                else:
                    mic_arg = self._resolve_windows_device_name(mic)
            else:
                mic_arg = None

            cmd = self._build_windows_command(loopback_arg, mic_arg)
        elif is_linux():
            cmd = self._build_linux_command(loopback, mic)
        else:
            raise FFmpegRuntimeError("Unsupported platform for audio capture")

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=create_no_window_flags()
            )

            logger.info(f"FFmpeg process started (PID: {self._process.pid})")
            logger.info(f"Recording to: {self.wav_path}")

            time.sleep(0.5)
            if self._process.poll() is not None:
                _, stderr_output = self._process.communicate()
                error_msg = stderr_output.decode("utf-8", errors="replace") if stderr_output else "Unknown error"
                logger.error(f"FFmpeg process died immediately. Exit code: {self._process.returncode}")
                logger.error(f"FFmpeg stderr: {error_msg}")
                raise FFmpegRuntimeError("FFmpeg failed to start recording. Check the log file for details.")

        except FFmpegRuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to start FFmpeg process: {e}")
            raise FFmpegRuntimeError(str(e))

        return self.wav_path

    def stop(self) -> str:
        if self._process and self._process.poll() is None:
            try:
                self._process.communicate(input=b"q", timeout=5)
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
            raise FFmpegRuntimeError("Recording failed: Output file does not exist.")

        file_size = os.path.getsize(self.wav_path)
        if file_size == 0:
            raise FFmpegRuntimeError("Recording failed: Output file is empty.")

        logger.info(f"Recording stopped successfully. File size: {file_size} bytes")
        return self.wav_path
