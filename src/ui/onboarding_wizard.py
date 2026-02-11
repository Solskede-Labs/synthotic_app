import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.constants import THEME_COLORS, LANG_TEXTS, BASE_DIR, VERSION
from src.core.audio_engine import AudioEngine


class OnboardingWizard(tk.Toplevel):
    """
    First-run onboarding wizard - matches main app design
    """
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.cfg = config
        self.parent_app = parent
        
        # Window setup
        self.title("Synthotic - Setup Inicial")
        self.geometry("620x600")
        self.configure(bg=THEME_COLORS["bg"])
        self.resizable(False, False)
        
        if parent:
            self.transient(parent)
        
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # State
        self.current_page = 0
        self.total_pages = 4  # Welcome+Lang, Folder, Devices, Confirmation
        
        # Selections
        self.selected_folder = tk.StringVar(value=BASE_DIR)
        self.selected_loopback = tk.StringVar()
        self.selected_mic = tk.StringVar()
        self.selected_lang = tk.StringVar(value=self.cfg.get("language") or "pt_BR")
        
        # Audio engine
        self.engine = AudioEngine()
        self.devices_list = []
        
        self.pages = []
        self.setup_ui()
        self.show_page(0)
    
    def get_text(self, key):
        """Get localized text"""
        lang = self.selected_lang.get()
        return LANG_TEXTS.get(lang, LANG_TEXTS["pt_BR"]).get(key, key)
    
    def setup_ui(self):
        # Header (like main app)
        header_frm = tk.Frame(self, bg=THEME_COLORS["surface"], height=70)
        header_frm.pack(fill="x")
        header_frm.pack_propagate(False)
        
        tk.Label(
            header_frm,
            text="SYNTHOTIC",
            font=("Segoe UI", 20, "bold"),
            bg=THEME_COLORS["surface"],
            fg="white"
        ).pack(side="left", padx=25, pady=15)
        
        tk.Label(
            header_frm,
            text=f"v{VERSION}",
            font=("Segoe UI", 9),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["primary"]
        ).pack(side="left", pady=(22,15))
        
        self.progress_label = tk.Label(
            header_frm,
            text="",
            font=("Segoe UI", 10),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text_dim"]
        )
        self.progress_label.pack(side="right", padx=25)
        
        # Content area
        self.content_frame = tk.Frame(self, bg=THEME_COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Create pages
        self.pages.append(self.create_welcome_page())
        self.pages.append(self.create_folder_page())
        self.pages.append(self.create_devices_page())
        self.pages.append(self.create_confirmation_page())
        
        # Bottom buttons (like main app footer style)
        nav_frame = tk.Frame(self, bg=THEME_COLORS["bg"])
        nav_frame.pack(side="bottom", fill="x", padx=40, pady=(10, 25))
        
        # Create buttons with hover effect support
        self.btn_back = tk.Button(
            nav_frame,
            text="← Voltar",
            command=self.go_back,
            bg=THEME_COLORS["secondary"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=20,
            pady=12,
            state="disabled"
        )
        self.btn_back.pack(side="left")
        
        self.btn_next = tk.Button(
            nav_frame,
            text="Próximo →",
            command=self.go_next,
            bg=THEME_COLORS["primary"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=20,
            pady=12
        )
        self.btn_next.pack(side="right")
        
        # Add hover effects
        def on_enter_next(e):
            if self.btn_next['state'] != 'disabled':
                self.btn_next.config(bg="#00FF88")
        
        def on_leave_next(e):
            if self.btn_next['state'] != 'disabled':
                # Check if it's the finish button (green) or next button
                if self.current_page == self.total_pages - 1:
                    self.btn_next.config(bg="#4CAF50")
                else:
                    self.btn_next.config(bg=THEME_COLORS["primary"])
        
        def on_enter_back(e):
            if self.btn_back['state'] != 'disabled':
                self.btn_back.config(bg="#383838")
        
        def on_leave_back(e):
            if self.btn_back['state'] != 'disabled':
                self.btn_back.config(bg=THEME_COLORS["secondary"])
        
        self.btn_next.bind("<Enter>", on_enter_next)
        self.btn_next.bind("<Leave>", on_leave_next)
        self.btn_back.bind("<Enter>", on_enter_back)
        self.btn_back.bind("<Leave>", on_leave_back)
    
    def create_welcome_page(self):
        page = tk.Frame(self.content_frame, bg=THEME_COLORS["bg"])
        
        # Title
        tk.Label(
            page,
            text="Bem-vindo ao Synthotic!",
            font=("Segoe UI", 20, "bold"),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text"]
        ).pack(pady=(50, 15))
        
        tk.Label(
            page,
            text="Configure em 3 passos rápidos",
            font=("Segoe UI", 12),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text_dim"]
        ).pack(pady=(0, 50))
        
        # Language selector
        lang_frame = tk.Frame(page, bg=THEME_COLORS["surface"], bd=1, relief="solid")
        lang_frame.pack(fill="x", pady=20)
        
        lang_inner = tk.Frame(lang_frame, bg=THEME_COLORS["surface"])
        lang_inner.pack(padx=30, pady=30)
        
        tk.Label(
            lang_inner,
            text="🌐 Idioma / Language:",
            font=("Segoe UI", 12, "bold"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"]
        ).pack(anchor="w", pady=(0, 15))
        
        lang_combo = ttk.Combobox(
            lang_inner,
            textvariable=self.selected_lang,
            values=["pt_BR", "en_US"],
            state="readonly",
            width=35,
            font=("Segoe UI", 11)
        )
        lang_combo.pack(anchor="w")
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self.update_language())
        
        # Instructions
        self.lbl_welcome_instructions = tk.Label(
            page,
            text="Selecione o idioma e clique em 'Próximo' para começar",
            font=("Segoe UI", 10),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text_dim"]
        )
        self.lbl_welcome_instructions.pack(pady=(40, 0))
        
        return page
    
    def create_folder_page(self):
        page = tk.Frame(self.content_frame, bg=THEME_COLORS["bg"])
        
        # Title
        self.lbl_folder_title = tk.Label(
            page,
            text="Pasta de Saída",
            font=("Segoe UI", 18, "bold"),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_folder_title.pack(pady=(40, 10))
        
        self.lbl_folder_subtitle = tk.Label(
            page,
            text="Onde deseja salvar as gravações e transcrições?",
            font=("Segoe UI", 11),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text_dim"]
        )
        self.lbl_folder_subtitle.pack(pady=(0, 60))
        
        # Folder selector
        folder_frame = tk.Frame(page, bg=THEME_COLORS["surface"], bd=1, relief="solid")
        folder_frame.pack(fill="x", pady=20)
        
        folder_inner = tk.Frame(folder_frame, bg=THEME_COLORS["surface"])
        folder_inner.pack(padx=30, pady=30)
        
        self.lbl_folder = tk.Label(
            folder_inner,
            text="📂 Pasta de Saída:",
            font=("Segoe UI", 11, "bold"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_folder.pack(anchor="w", pady=(0, 15))
        
        entry_row = tk.Frame(folder_inner, bg=THEME_COLORS["surface"])
        entry_row.pack(fill="x")
        
        folder_entry = tk.Entry(
            entry_row,
            textvariable=self.selected_folder,
            bg=THEME_COLORS["secondary"],
            fg=THEME_COLORS["text"],
            font=("Segoe UI", 10),
            bd=1,
            relief="solid"
        )
        folder_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 15))
        
        self.btn_browse = tk.Button(
            entry_row,
            text="Procurar...",
            command=self.browse_folder,
            bg="#555555",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=18,
            pady=8
        )
        self.btn_browse.pack(side="left")
        
        # Hover effect for browse button
        self.btn_browse.bind("<Enter>", lambda e: self.btn_browse.config(bg="#777777"))
        self.btn_browse.bind("<Leave>", lambda e: self.btn_browse.config(bg="#555555"))
        
        return page
    
    def create_devices_page(self):
        page = tk.Frame(self.content_frame, bg=THEME_COLORS["bg"])
        
        # Title
        self.lbl_devices_title = tk.Label(
            page,
            text="Selecione os Dispositivos de Áudio",
            font=("Segoe UI", 16, "bold"),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_devices_title.pack(pady=(20, 10))
        
        self.lbl_devices_subtitle = tk.Label(
            page,
            text="Escolha o dispositivo de áudio do sistema e o microfone",
            font=("Segoe UI", 10),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text_dim"]
        )
        self.lbl_devices_subtitle.pack(pady=(0, 20))
        
        # Devices frame
        devices_frame = tk.Frame(page, bg=THEME_COLORS["surface"], bd=1, relief="solid")
        devices_frame.pack(fill="both", expand=True, pady=10)
        
        devices_inner = tk.Frame(devices_frame, bg=THEME_COLORS["surface"])
        devices_inner.pack(padx=25, pady=25, fill="both", expand=True)
        
        # Loopback
        self.lbl_loopback = tk.Label(
            devices_inner,
            text="🔊 Áudio do Sistema (Loopback):",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_loopback.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.loopback_combo = ttk.Combobox(
            devices_inner,
            textvariable=self.selected_loopback,
            state="readonly",
            width=60,
            font=("Segoe UI", 9)
        )
        self.loopback_combo.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        # Microphone
        self.lbl_mic = tk.Label(
            devices_inner,
            text="🎤 Microfone:",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_mic.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.mic_combo = ttk.Combobox(
            devices_inner,
            textvariable=self.selected_mic,
            state="readonly",
            width=60,
            font=("Segoe UI", 9)
        )
        self.mic_combo.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        
        # Refresh button
        self.btn_refresh = tk.Button(
            devices_inner,
            text="🔄 Atualizar Dispositivos",
            command=self.refresh_devices,
            bg="#555555",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=18,
            pady=8
        )
        self.btn_refresh.grid(row=4, column=0, pady=(10, 5))
        
        # Hover effect for refresh button
        self.btn_refresh.bind("<Enter>", lambda e: self.btn_refresh.config(bg="#777777"))
        self.btn_refresh.bind("<Leave>", lambda e: self.btn_refresh.config(bg="#555555"))
        
        self.devices_status_label = tk.Label(
            devices_inner,
            text="",
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text_dim"],
            font=("Segoe UI", 8)
        )
        self.devices_status_label.grid(row=5, column=0, pady=(5, 0))
        
        devices_inner.grid_columnconfigure(0, weight=1)
        
        # Load devices when shown
        self.after(200, self.refresh_devices)
        
        return page
    
    def create_confirmation_page(self):
        page = tk.Frame(self.content_frame, bg=THEME_COLORS["bg"])
        
        # Title
        self.lbl_confirm_title = tk.Label(
            page,
            text="Confirme as Configurações",
            font=("Segoe UI", 16, "bold"),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text"]
        )
        self.lbl_confirm_title.pack(pady=(20, 10))
        
        self.lbl_confirm_subtitle = tk.Label(
            page,
            text="Revise suas escolhas antes de começar",
            font=("Segoe UI", 10),
            bg=THEME_COLORS["bg"],
            fg=THEME_COLORS["text_dim"]
        )
        self.lbl_confirm_subtitle.pack(pady=(0, 20))
        
        # Summary frame
        summary_frame = tk.Frame(page, bg=THEME_COLORS["surface"], bd=1, relief="solid")
        summary_frame.pack(fill="both", expand=True, pady=10)
        
        summary_inner = tk.Frame(summary_frame, bg=THEME_COLORS["surface"])
        summary_inner.pack(padx=30, pady=30, fill="both", expand=True)
        
        self.summary_text = tk.Label(
            summary_inner,
            text="",
            font=("Segoe UI", 10),
            bg=THEME_COLORS["surface"],
            fg=THEME_COLORS["text"],
            justify="left",
            anchor="nw"
        )
        self.summary_text.pack(fill="both", expand=True)
        
        return page
    
    def browse_folder(self):
        folder = filedialog.askdirectory(
            parent=self,
            initialdir=self.selected_folder.get(),
            title="Selecione a pasta"
        )
        if folder:
            self.selected_folder.set(folder)
    
    def refresh_devices(self):
        self.devices_status_label.config(text="Carregando...")
        self.update()
        
        try:
            self.devices_list = self.engine.get_ffmpeg_devices()
            audio_devices = [d for d in self.devices_list if d["type"] == "audio"]
            device_names = [d["friendly_name"] for d in audio_devices]
            
            self.loopback_combo['values'] = device_names
            self.mic_combo['values'] = device_names
            
            # Pre-select
            if device_names:
                if not self.selected_loopback.get():
                    self.selected_loopback.set(device_names[0])
                if not self.selected_mic.get():
                    self.selected_mic.set(device_names[1] if len(device_names) > 1 else device_names[0])
            
            self.devices_status_label.config(text=f"{len(audio_devices)} dispositivos encontrados")
        except Exception as e:
            self.devices_status_label.config(text=f"Erro: {str(e)}")
    
    def update_language(self):
        """Update UI text when language changes"""
        lang = self.selected_lang.get()
        
        # Update button texts
        if lang == "pt_BR":
            self.btn_back.config(text="← Voltar")
            self.btn_next.config(text="Próximo →" if self.current_page < 3 else "Iniciar Synthotic ✓")
            self.lbl_welcome_instructions.config(text="Selecione o idioma e clique em 'Próximo' para começar")
            self.lbl_folder_title.config(text="Pasta de Saída")
            self.lbl_folder_subtitle.config(text="Onde deseja salvar as gravações e transcrições?")
            self.lbl_folder.config(text="📂 Pasta de Saída:")
            self.btn_browse.config(text="Procurar...")
            self.lbl_devices_title.config(text="Selecione os Dispositivos de Áudio")
            self.lbl_devices_subtitle.config(text="Escolha o dispositivo de áudio do sistema e o microfone")
            self.lbl_loopback.config(text="🔊 Áudio do Sistema (Loopback):")
            self.lbl_mic.config(text="🎤 Microfone:")
            self.btn_refresh.config(text="🔄 Atualizar Dispositivos")
            self.lbl_confirm_title.config(text="Confirme as Configurações")
            self.lbl_confirm_subtitle.config(text="Revise suas escolhas antes de começar")
        else:
            self.btn_back.config(text="← Back")
            self.btn_next.config(text="Next →" if self.current_page < 3 else "Start Synthotic ✓")
            self.lbl_welcome_instructions.config(text="Select your language and click 'Next' to begin")
            self.lbl_folder_title.config(text="Output Folder")
            self.lbl_folder_subtitle.config(text="Where do you want to save recordings and transcriptions?")
            self.lbl_folder.config(text="📂 Output Folder:")
            self.btn_browse.config(text="Browse...")
            self.lbl_devices_title.config(text="Select Audio Devices")
            self.lbl_devices_subtitle.config(text="Choose your system audio and microphone")
            self.lbl_loopback.config(text="🔊 System Audio (Loopback):")
            self.lbl_mic.config(text="🎤 Microphone:")
            self.btn_refresh.config(text="🔄 Refresh Devices")
            self.lbl_confirm_title.config(text="Confirm Settings")
            self.lbl_confirm_subtitle.config(text="Review your choices before starting")
        
        self.update_progress_label()
        if self.current_page == 3:
            self.update_confirmation_summary()
    
    def update_progress_label(self):
        lang = self.selected_lang.get()
        if lang == "pt_BR":
            self.progress_label.config(text=f"Passo {self.current_page + 1} de {self.total_pages}")
        else:
            self.progress_label.config(text=f"Step {self.current_page + 1} of {self.total_pages}")
    
    def show_page(self, page_num):
        # Hide all
        for page in self.pages:
            page.pack_forget()
        
        # Show current
        self.pages[page_num].pack(fill="both", expand=True)
        
        # Update progress
        self.update_progress_label()
        
        # Update buttons
        self.btn_back.config(state="normal" if page_num > 0 else "disabled")
        
        lang = self.selected_lang.get()
        if page_num == self.total_pages - 1:  # Page 3 (confirmation)
            # Last page
            finish_text = "Iniciar Synthotic ✓" if lang == "pt_BR" else "Start Synthotic ✓"
            self.btn_next.config(
                text=finish_text,
                bg="#4CAF50",
                command=self.finish_wizard
            )
        else:
            next_text = "Próximo →" if lang == "pt_BR" else "Next →"
            self.btn_next.config(
                text=next_text,
                bg=THEME_COLORS["primary"],
                command=self.go_next
            )
        
        # Update confirmation if last page
        if page_num == 3:
            self.update_confirmation_summary()
    
    def update_confirmation_summary(self):
        lang = self.selected_lang.get()
        
        if lang == "pt_BR":
            summary = f"""✓ Pasta de Saída:
   {self.selected_folder.get()}

✓ Áudio do Sistema:
   {self.selected_loopback.get()}

✓ Microfone:
   {self.selected_mic.get()}

✓ Idioma:
   {"Português (Brasil)" if self.selected_lang.get() == "pt_BR" else "English (US)"}
"""
        else:
            summary = f"""✓ Output Folder:
   {self.selected_folder.get()}

✓ System Audio:
   {self.selected_loopback.get()}

✓ Microphone:
   {self.selected_mic.get()}

✓ Language:
   {"Português (Brasil)" if self.selected_lang.get() == "pt_BR" else "English (US)"}
"""
        
        self.summary_text.config(text=summary)
    
    def validate_current_page(self):
        lang = self.selected_lang.get()
        
        if self.current_page == 1:  # Folder page
            folder = self.selected_folder.get()
            if not folder:
                msg = "Por favor, selecione uma pasta válida." if lang == "pt_BR" else "Please select a valid folder."
                title = "Erro" if lang == "pt_BR" else "Error"
                messagebox.showerror(title, msg)
                return False
        
        elif self.current_page == 2:  # Devices page
            if not self.selected_loopback.get() or not self.selected_mic.get():
                msg = "Por favor, selecione ambos os dispositivos de áudio." if lang == "pt_BR" else "Please select both audio devices."
                title = "Erro" if lang == "pt_BR" else "Error"
                messagebox.showerror(title, msg)
                return False
        
        return True
    
    def go_next(self):
        if not self.validate_current_page():
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_page(self.current_page)
    
    def go_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)
    
    def finish_wizard(self):
        if not self.validate_current_page():
            return
        
        # Save folder
        output_folder = self.selected_folder.get()
        if output_folder != BASE_DIR:
            self.cfg.set("output_folder", output_folder)
            os.makedirs(output_folder, exist_ok=True)
        
        # Save device GUIDs
        for d in self.devices_list:
            if d["friendly_name"] == self.selected_loopback.get():
                self.cfg.set("loopback_device_guid", d["alternative_name"])
                break
        
        for d in self.devices_list:
            if d["friendly_name"] == self.selected_mic.get():
                self.cfg.set("mic_device_guid", d["alternative_name"])
                break
        
        # Save language
        self.cfg.set("language", self.selected_lang.get())
        
        # Mark complete
        self.cfg.set("first_run", False)
        
        # Close
        self.grab_release()
        self.destroy()
    
    def on_cancel(self):
        lang = self.selected_lang.get()
        
        if lang == "pt_BR":
            response = messagebox.askyesno(
                "Cancelar Configuração",
                "Tem certeza que deseja cancelar?\nO Synthotic precisa ser configurado antes do primeiro uso.",
                parent=self
            )
        else:
            response = messagebox.askyesno(
                "Cancel Setup",
                "Are you sure you want to cancel?\nSynthotic needs to be configured before first use.",
                parent=self
            )
        
        if response:
            self.grab_release()
            self.destroy()
