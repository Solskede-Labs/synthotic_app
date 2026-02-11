import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from src.constants import THEME_COLORS, BASE_DIR
from src.core.audio_engine import AudioEngine


class SettingsWindow(tk.Toplevel):
    
    def __init__(self, parent, config, audio_engine):
        super().__init__(parent)
        self.parent = parent
        self.cfg = config
        self.engine = audio_engine
        
        self.title(self.get_text("settings_title"))
        try:
            self.iconbitmap(parent.iconbitmap())
        except Exception:
            pass
            
        self.geometry("650x550")
        self.configure(bg=THEME_COLORS["bg"])
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.devices_list = []
        self.setup_ui()
        self.load_current_settings()
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
    def get_text(self, key):
        lang = self.cfg.get("language")
        from src.constants import LANG_TEXTS
        return LANG_TEXTS.get(lang, LANG_TEXTS["en_US"]).get(key, key)
    
    def setup_ui(self):
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(self, bg=THEME_COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # Create the main frame inside canvas
        main_frame = tk.Frame(canvas, bg=THEME_COLORS["bg"])
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=20)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Update scroll region when frame changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind("<Configure>", on_frame_configure)
        
        # Bind mousewheel for scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header
        header = tk.Label(
            main_frame, 
            text=self.get_text("settings_title"),
            font=("Segoe UI", 18, "bold"),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text"]
        )
        header.pack(pady=(0, 20))
        
        # === AUDIO DEVICES SECTION ===
        audio_section = tk.LabelFrame(
            main_frame,
            text=self.get_text("settings_audio"),
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLORS["surface"],
            fg="#888888",
            bd=1,
            relief="solid"
        )
        audio_section.pack(fill="x", pady=(0, 15))
        
        audio_inner = tk.Frame(audio_section, bg=THEME_COLORS["surface"])
        audio_inner.pack(padx=15, pady=15)
        
        # Loopback device
        tk.Label(
            audio_inner,
            text=self.get_text("settings_loopback"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.loopback_var = tk.StringVar()
        self.loopback_combo = ttk.Combobox(
            audio_inner,
            textvariable=self.loopback_var,
            state="readonly",
            width=55,
            font=("Segoe UI", 9)
        )
        self.loopback_combo.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        # Microphone device
        tk.Label(
            audio_inner,
            text=self.get_text("settings_mic"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 9)
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(
            audio_inner,
            textvariable=self.mic_var,
            state="readonly",
            width=55,
            font=("Segoe UI", 9)
        )
        self.mic_combo.grid(row=3, column=0, pady=(0, 10), sticky="ew")
        
        # Refresh button
        refresh_btn = tk.Button(
            audio_inner,
            text=self.get_text("settings_refresh"),
            command=self.refresh_devices,
            bg="#555555",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            padx=15,
            pady=6
        )
        refresh_btn.grid(row=4, column=0, pady=(5, 5))
        
        self.refresh_label = tk.Label(
            audio_inner,
            text="",
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text_dim"],
            font=("Segoe UI", 8)
        )
        self.refresh_label.grid(row=5, column=0, pady=(0, 5))
        
        # === OUTPUT FOLDER SECTION ===
        folder_section = tk.LabelFrame(
            main_frame,
            text=self.get_text("settings_folder"),
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLORS["surface"],
            fg="#888888",
            bd=1,
            relief="solid"
        )
        folder_section.pack(fill="x", pady=(0, 15))
        
        folder_inner = tk.Frame(folder_section, bg=THEME_COLORS["surface"])
        folder_inner.pack(padx=15, pady=15)
        
        tk.Label(
            folder_inner,
            text=self.get_text("settings_folder_label"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 5))
        
        folder_row = tk.Frame(folder_inner, bg=THEME_COLORS["surface"])
        folder_row.pack(fill="x")
        
        self.folder_var = tk.StringVar()
        folder_entry = tk.Entry(
            folder_row,
            textvariable=self.folder_var,
            bg=THEME_COLORS["secondary"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 9),
            bd=1,
            relief="solid",
            width=48
        )
        folder_entry.pack(side="left", padx=(0, 10), ipady=3)
        
        browse_btn = tk.Button(
            folder_row,
            text=self.get_text("settings_browse"),
            command=self.browse_folder,
            bg="#555555",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            padx=12,
            pady=6
        )
        browse_btn.pack(side="left")
        
        # === LANGUAGE SECTION ===
        lang_section = tk.LabelFrame(
            main_frame,
            text=self.get_text("lbl_lang"),
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLORS["surface"],
            fg="#888888",
            bd=1,
            relief="solid"
        )
        lang_section.pack(fill="x", pady=(0, 20))
        
        lang_inner = tk.Frame(lang_section, bg=THEME_COLORS["surface"])
        lang_inner.pack(padx=15, pady=15, fill="x")
        
        # Language combobox with explicit font and width
        self.lang_var = tk.StringVar(value=self.cfg.get("language"))
        self.lang_combo = ttk.Combobox(
            lang_inner,
            textvariable=self.lang_var,
            values=["pt_BR", "en_US"],
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        self.lang_combo.pack(anchor="w", pady=5)
        
        # === RE-RUN WIZARD BUTTON ===
        wizard_frame = tk.Frame(main_frame, bg=THEME_COLORS["bg"])
        wizard_frame.pack(pady=(15, 0))
        
        wizard_btn = tk.Button(
            wizard_frame,
            text="🔄 Re-executar Assistente de Configuração" if self.cfg.get("language") == "pt_BR" else "🔄 Re-run Setup Wizard",
            command=self.rerun_wizard,
            bg="#666666",
            fg="white",
            font=("Segoe UI", 9),
            cursor="hand2",
            bd=0,
            padx=15,
            pady=8
        )
        wizard_btn.pack()
        
        # === BOTTOM BUTTONS ===
        button_frame = tk.Frame(main_frame, bg=THEME_COLORS["bg"])
        button_frame.pack(pady=(10, 0))
        
        save_btn = tk.Button(
            button_frame,
            text=self.get_text("settings_save"),
            command=self.on_save,
            bg="#4A90E2",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            bd=0,
            width=18,
            height=2
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text=self.get_text("settings_cancel"),
            command=self.on_cancel,
            bg=THEME_COLORS["secondary"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            bd=0,
            width=18,
            height=2
        )
        cancel_btn.pack(side="left", padx=10)
    
    def load_current_settings(self):
        # Load folder
        current_folder = self.cfg.get("output_folder") or BASE_DIR
        self.folder_var.set(current_folder)
        
        # Load language
        self.lang_var.set(self.cfg.get("language") or "pt_BR")
        
        # Trigger device refresh in background
        threading.Thread(target=self.refresh_devices, daemon=True).start()
    
    def refresh_devices(self):
        self.refresh_label.config(text="Carregando dispositivos...")
        self.update()
        
        # Save current selections before refreshing
        current_loopback = self.loopback_var.get()
        current_mic = self.mic_var.get()
        
        try:
            self.devices_list = self.engine.get_ffmpeg_devices()
            
            # Filter audio devices
            audio_devices = [d for d in self.devices_list if d["type"] == "audio"]
            
            # Populate dropdowns
            auto_option = self.get_text("settings_auto_detect")
            device_names = [auto_option] + [d["friendly_name"] for d in audio_devices]
            
            self.loopback_combo['values'] = device_names
            self.mic_combo['values'] = device_names
            
            # Restore saved selections from config OR preserve current UI selections
            saved_loopback_guid = self.cfg.get("loopback_device_guid")
            saved_mic_guid = self.cfg.get("mic_device_guid")
            
            # Loopback device
            if current_loopback and current_loopback in device_names and current_loopback != auto_option:
                # Preserve current UI selection if it's not auto
                self.loopback_var.set(current_loopback)
            elif saved_loopback_guid:
                # Restore from config
                found = False
                for d in audio_devices:
                    if d["alternative_name"] == saved_loopback_guid:
                        self.loopback_var.set(d["friendly_name"])
                        found = True
                        break
                if not found:
                    self.loopback_var.set(auto_option)
            else:
                self.loopback_var.set(auto_option)
            
            # Microphone device
            if current_mic and current_mic in device_names and current_mic != auto_option:
                # Preserve current UI selection if it's not auto
                self.mic_var.set(current_mic)
            elif saved_mic_guid:
                # Restore from config
                found = False
                for d in audio_devices:
                    if d["alternative_name"] == saved_mic_guid:
                        self.mic_var.set(d["friendly_name"])
                        found = True
                        break
                if not found:
                    self.mic_var.set(auto_option)
            else:
                self.mic_var.set(auto_option)
            
            self.refresh_label.config(
                text=f"{len(audio_devices)} dispositivos encontrados"
            )
            
        except Exception as e:
            self.refresh_label.config(text=f"Erro: {str(e)}")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(
            parent=self,
            initialdir=self.folder_var.get(),
            title=self.get_text("settings_browse")
        )
        if folder:
            self.folder_var.set(folder)
    
    def on_save(self):
        # Save folder
        output_folder = self.folder_var.get()
        if output_folder and output_folder != BASE_DIR:
            self.cfg.set("output_folder", output_folder)
            os.makedirs(output_folder, exist_ok=True)
        else:
            self.cfg.set("output_folder", None)
        
        # Save language
        old_lang = self.cfg.get("language")
        new_lang = self.lang_var.get()
        if old_lang != new_lang:
            self.cfg.set("language", new_lang)
            self.parent.refresh_ui_text()
        
        # Save audio devices
        auto_option = self.get_text("settings_auto_detect")
        
        loopback_selection = self.loopback_var.get()
        if loopback_selection and loopback_selection != auto_option:
            for d in self.devices_list:
                if d["friendly_name"] == loopback_selection:
                    self.cfg.set("loopback_device_guid", d["alternative_name"])
                    break
        else:
            self.cfg.set("loopback_device_guid", None)
        
        mic_selection = self.mic_var.get()
        if mic_selection and mic_selection != auto_option:
            for d in self.devices_list:
                if d["friendly_name"] == mic_selection:
                    self.cfg.set("mic_device_guid", d["alternative_name"])
                    break
        else:
            self.cfg.set("mic_device_guid", None)
        
        # Show confirmation
        messagebox.showinfo(
            "Configurações Salvas" if new_lang == "pt_BR" else "Settings Saved",
            "As configurações foram salvas com sucesso!" if new_lang == "pt_BR" else "Settings saved successfully!"
        )
        
        self.grab_release()
        self.destroy()
    
    
    def on_cancel(self):
        self.grab_release()
        self.destroy()
    
    def rerun_wizard(self):
        """Re-launch the onboarding wizard"""
        from src.ui.onboarding_wizard import OnboardingWizard
        
        # Set first_run to trigger wizard
        self.cfg.set("first_run", True)
        
        # Close settings
        self.grab_release()
        self.destroy()
        
        # Launch wizard
        OnboardingWizard(self.parent, self.cfg)

