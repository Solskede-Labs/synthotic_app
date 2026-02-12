import os
import queue
import shutil
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from src.constants import APP_NAME, VERSION, BASE_DIR, THEME_COLORS, LANG_TEXTS
from src.core.audio_engine import AudioEngine, LoopbackNotFoundError, FFmpegRuntimeError
from src.core.transcriber import transcription_worker
from src.ui.welcome_window import WelcomeWindow
from src.ui.about_window import AboutWindow
from src.ui.settings_window import SettingsWindow
from src.ui.tray import TrayManager
from src.utils import get_resource_path
from src.platform_utils import open_audio_settings, open_path

class DashboardApp(tk.Tk):
    
    def __init__(self, config):
        super().__init__()
        self.cfg = config
        
        self.title(APP_NAME)
        try:
            self.iconbitmap(get_resource_path("app.ico"))
        except Exception:
            pass
            
        self.geometry("620x450")
        self.configure(bg=THEME_COLORS["bg"])
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        self.engine = AudioEngine()
        self.is_recording = False
        
        self.gui_queue = queue.Queue()
        
        self.setup_ui()
        
        self.tray = TrayManager(
            command_queue=self.gui_queue,
            restore_callback=self.restore_from_tray,
            exit_callback=self.quit_app,
            config=self.cfg
        )
        threading.Thread(target=self.tray.run, daemon=True).start()
        
        self.after(500, self.check_first_run)
        
        self.check_queue()

    def check_first_run(self):
        if self.cfg.get("first_run"):
            WelcomeWindow(self, self.cfg)

    def get_text(self, key):
        lang = self.cfg.get("language")
        return LANG_TEXTS.get(lang, LANG_TEXTS["en_US"]).get(key, key)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Synthotic.Horizontal.TProgressbar", 
            foreground=THEME_COLORS["primary"], 
            background=THEME_COLORS["primary"], 
            troughcolor=THEME_COLORS["surface"], 
            thickness=8
        )
        
        self.option_add('*TCombobox*Listbox.background', THEME_COLORS["surface"])
        self.option_add('*TCombobox*Listbox.foreground', THEME_COLORS["text"])
        
        header_frm = tk.Frame(self, bg=THEME_COLORS["surface"], height=70)
        header_frm.pack(fill="x")
        
        tk.Label(header_frm, text="SYNTHOTIC", font=("Segoe UI", 20, "bold"), bg=THEME_COLORS["surface"], fg="white").pack(side="left", padx=25, pady=15)
        tk.Label(header_frm, text=f"v{VERSION}", font=("Segoe UI", 9), bg=THEME_COLORS["surface"], fg=THEME_COLORS["primary"]).pack(side="left", pady=(22, 15))
        
        # Settings button
        settings_btn = tk.Button(
            header_frm,
            text="⚙",
            font=("Segoe UI", 16),
            bg=THEME_COLORS["surface"],
            fg="#888888",
            activebackground=THEME_COLORS["surface"],
            activeforeground="#AAAAAA",
            bd=0,
            cursor="hand2",
            command=self.open_settings
        )
        settings_btn.pack(side="right", padx=20)
        
        main_frm = tk.Frame(self, bg=THEME_COLORS["bg"])
        main_frm.pack(fill="both", expand=True, padx=40, pady=30)
        
        self.lbl_status = tk.Label(main_frm, text="", font=("Segoe UI", 16), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text"])
        self.lbl_status.pack(pady=(10, 5))
        
        self.lbl_substatus = tk.Label(main_frm, text="", font=("Segoe UI", 10), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"])
        self.lbl_substatus.pack(pady=(0, 25))
        
        self.progress = ttk.Progressbar(main_frm, style="Synthotic.Horizontal.TProgressbar", orient="horizontal", length=520, mode="determinate")
        self.progress.pack(pady=10)
        
        btn_frm = tk.Frame(main_frm, bg=THEME_COLORS["bg"])
        btn_frm.pack(pady=30)

        self.btn_rec = self.create_flat_button(btn_frm, "", THEME_COLORS["rec"], self.toggle_recording)
        self.btn_rec.grid(row=0, column=0, padx=15)

        self.btn_import = self.create_flat_button(btn_frm, "", "#3498db", self.import_file)
        self.btn_import.grid(row=0, column=1, padx=15)
        
        footer_frm = tk.Frame(self, bg=THEME_COLORS["bg"])
        footer_frm.pack(side="bottom", fill="x", pady=20, padx=25)

        self.btn_folder = tk.Button(footer_frm, text="", command=lambda: open_path(BASE_DIR),
                  bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"], activebackground=THEME_COLORS["bg"], activeforeground="white",
                  bd=0, font=("Segoe UI", 9, "underline"), cursor="hand2")
        self.btn_folder.pack(side="right")

        self.btn_about = tk.Button(footer_frm, text="About", command=self.open_about,
                  bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"], activebackground=THEME_COLORS["bg"], activeforeground="white",
                  bd=0, font=("Segoe UI", 9, "underline"), cursor="hand2")
        self.btn_about.pack(side="right", padx=15)

        self.refresh_ui_text()

    def create_flat_button(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), bg=color, fg="white",
                        width=22, height=2, command=command, bd=0, relief="flat", cursor="hand2",
                        activebackground=color, activeforeground="white")
        return btn

    def refresh_ui_text(self):
        self.btn_folder.config(text=self.get_text("link_folder"))
        self.btn_about.config(text=self.get_text("tray_about").replace("ℹ️ ", ""))
        self.btn_import.config(text=self.get_text("btn_import"))
        
        if not self.is_recording:
            self.lbl_status.config(text=self.get_text("status_ready"))
            self.lbl_substatus.config(text=self.get_text("sub_ready"))
            self.btn_rec.config(text=self.get_text("btn_rec_start"), bg=THEME_COLORS["rec"])
        else:
            self.lbl_status.config(text=self.get_text("status_rec"))
            self.lbl_substatus.config(text=self.get_text("sub_rec"))
            self.btn_rec.config(text=self.get_text("btn_rec_stop"), bg="#f1c40f", fg="black")


    def toggle_recording(self):
        if not self.is_recording:
            try:
                self.engine.start()
                self.is_recording = True
                self.btn_import.config(state="disabled")
                self.progress['value'] = 0
                self.refresh_ui_text()
                self.tray.update_state("rec")
            except LoopbackNotFoundError:
                response = messagebox.askyesno(
                    self.get_text("err_loopback_title"),
                    self.get_text("err_loopback_msg")
                )
                if response:
                    open_audio_settings()
            except FFmpegRuntimeError as e:
                messagebox.showerror(
                    self.get_text("err_ffmpeg_title"),
                    self.get_text("err_ffmpeg_msg")
                )
        else:
            self.is_recording = False
            self.btn_rec.config(state="disabled")
            self.lbl_status.config(text="Finalizando...")
            threading.Thread(target=self.async_stop_live, daemon=True).start()

    def async_stop_live(self):
        wav_path = self.engine.stop()
        transcription_worker(wav_path, self.gui_queue, self.cfg)

    def import_file(self):
        file_path = filedialog.askopenfilename(parent=self, filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.flac")])
        if file_path:
            self.btn_rec.config(state="disabled")
            self.btn_import.config(state="disabled")
            
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            imp_dir = os.path.join(BASE_DIR, f"Import_{ts}")
            os.makedirs(imp_dir, exist_ok=True)
            dest = os.path.join(imp_dir, os.path.basename(file_path))
            
            self.lbl_status.config(text="Copiando arquivo...")
            self.update()
            shutil.copy2(file_path, dest)
            threading.Thread(target=transcription_worker, args=(dest, self.gui_queue, self.cfg, True), daemon=True).start()

    def check_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                
                if msg_type == "cmd_start":
                    if not self.is_recording: self.toggle_recording()
                elif msg_type == "cmd_stop":
                    if self.is_recording: self.toggle_recording()
                elif msg_type == "cmd_import":
                    if not self.is_recording: 
                        self.deiconify()
                        self.import_file()
                elif msg_type == "cmd_about":
                    self.deiconify()
                    self.open_about()
                
                elif msg_type == "status_proc":
                    self.lbl_status.config(text=self.get_text("status_proc"))
                    self.lbl_substatus.config(text=self.get_text("sub_proc"))
                    self.tray.update_state("proc")
                    
                elif msg_type == "progress":
                    self.progress['value'] = data
                    self.lbl_substatus.config(text=f"{self.get_text('sub_proc')} {data:.1f}%")
                    
                elif msg_type == "done":
                    self.lbl_status.config(text=self.get_text("status_done"))
                    self.lbl_substatus.config(text=self.get_text("sub_done"))
                    self.progress['value'] = 100
                    self.reset_ui()
                    self.tray.update_state("idle")
                    try:
                        open_path(data)
                        open_path(os.path.dirname(data))
                    except Exception: pass
                    self.deiconify()
                    self.lift()
                    
                elif msg_type == "error":
                    self.lbl_status.config(text=self.get_text("status_err"))
                    messagebox.showerror("Error", str(data))
                    self.reset_ui()
                    self.tray.update_state("idle")
                    
        except queue.Empty: pass
        finally: self.after(100, self.check_queue)

    def reset_ui(self):
        self.is_recording = False
        self.btn_rec.config(state="normal")
        self.btn_import.config(state="normal")
        self.refresh_ui_text()

    def hide_to_tray(self):
        self.withdraw()
        self.tray.notify(self.get_text("notify_min_title"), self.get_text("notify_min_msg"))

    def restore_from_tray(self, icon=None, item=None):
        self.deiconify()
        self.lift()

    def quit_app(self, icon=None, item=None):
        self.tray.stop()
        self.quit()

    def open_about(self):
        AboutWindow(self, self.cfg)
    
    def open_settings(self):
        SettingsWindow(self, self.cfg, self.engine)
