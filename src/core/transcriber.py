import os
import time
import logging
import traceback
import datetime

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

from src.constants import MODEL_SIZE

def transcription_worker(audio_path, gui_queue, config, is_import=False):
    if WhisperModel is None:
        gui_queue.put(("error", "Missing dependency: faster-whisper"))
        return

    try:
        gui_queue.put(("status_proc", None))
        
        user_lang = config.get("language")
        whisper_lang = "pt" if "pt" in user_lang else "en"
        
        prompt = (
            "Professional meeting transcription. Use formal punctuation and proper grammar. "
            "Maintain technical terminology and acronyms accurately."
        )

        try:
            audio_info = sf.info(audio_path)
            total_duration = audio_info.duration
        except Exception:
            total_duration = 1
        
        total_cores = os.cpu_count() or 2
        safe_threads = max(2, int(total_cores / 2))
        
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=safe_threads)
        
        segments, info = model.transcribe(
            audio_path, 
            beam_size=5, 
            initial_prompt=prompt,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            repetition_penalty=1.15,
            condition_on_previous_text=False
        )
        
        txt_path = os.path.splitext(audio_path)[0] + ".txt"
        
        with open(txt_path, "w", encoding="utf-8") as f:
            header = "SYNTHOTIC IMPORT REPORT\n" if is_import else "SYNTHOTIC LIVE REPORT\n"
            f.write(f"{header}Date: {datetime.datetime.now()}\n")
            f.write(f"File: {os.path.basename(audio_path)}\n{'-'*40}\n\n")
            
            for segment in segments:
                current_pos = segment.end
                percent = (current_pos / total_duration) * 100
                gui_queue.put(("progress", min(99, percent)))
                
                ts = time.strftime('%H:%M:%S', time.gmtime(segment.start))
                line = f"[{ts}] {segment.text}\n"
                f.write(line)
        
        gui_queue.put(("progress", 100))
        time.sleep(0.5)
        gui_queue.put(("done", txt_path))
        
    except Exception as e:
        gui_queue.put(("error", str(e)))
        logging.error(traceback.format_exc())
