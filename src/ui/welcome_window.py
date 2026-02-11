import tkinter as tk
import webbrowser
from src.constants import THEME_COLORS, LANG_TEXTS, DEV_NAME, MY_LINKEDIN, MY_GITHUB
from src.utils import get_resource_path

class WelcomeWindow(tk.Toplevel):
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.cfg = config
        self.title("Bem-vindo")
        try:
            self.iconbitmap(get_resource_path("app.ico"))
        except Exception:
            pass
            
        self.geometry("500x450")
        self.configure(bg=THEME_COLORS["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (500/2)
        y = (screen_height/2) - (450/2)
        self.geometry(f'+{int(x)}+{int(y)}')
        self.protocol("WM_DELETE_WINDOW", self.close_welcome)

        self.setup_ui()

    def get_text(self, key):
        lang = self.cfg.get("language")
        return LANG_TEXTS.get(lang, LANG_TEXTS["en_US"]).get(key, key)

    def setup_ui(self):
        header = tk.Frame(self, bg=THEME_COLORS["surface"], height=100)
        header.pack(fill="x")
        tk.Label(header, text="SYNTHOTIC", font=("Segoe UI", 24, "bold"), bg=THEME_COLORS["surface"], fg="white").pack(pady=(25, 5))
        tk.Label(header, text=self.get_text("welcome_head"), font=("Segoe UI", 10), bg=THEME_COLORS["surface"], fg=THEME_COLORS["primary"]).pack(pady=0)
        
        body_frm = tk.Frame(self, bg=THEME_COLORS["bg"])
        body_frm.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(body_frm, text=self.get_text("welcome_body"), font=("Segoe UI", 11), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text"], justify="center", wraplength=400).pack(pady=10)
        
        tk.Label(body_frm, text=self.get_text("welcome_dev"), font=("Segoe UI", 9, "bold"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"]).pack(pady=(20, 5))
        
        link_frm = tk.Frame(body_frm, bg=THEME_COLORS["bg"])
        link_frm.pack()
        
        lbl_link = tk.Label(link_frm, text=f"{DEV_NAME} (LinkedIn)", font=("Segoe UI", 10, "underline"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["link"], cursor="hand2")
        lbl_link.pack(pady=2)
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open(MY_LINKEDIN))
        
        lbl_git = tk.Label(link_frm, text="GitHub / Source Code", font=("Segoe UI", 10, "underline"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"], cursor="hand2")
        lbl_git.pack(pady=2)
        lbl_git.bind("<Button-1>", lambda e: webbrowser.open(MY_GITHUB))
        
        btn = tk.Button(self, text=self.get_text("welcome_btn"), font=("Segoe UI", 11, "bold"), bg=THEME_COLORS["primary"], fg="black",
                        width=25, height=2, bd=0, relief="flat", cursor="hand2", command=self.close_welcome)
        btn.pack(side="bottom", pady=30)

    def close_welcome(self):
        self.cfg.set("first_run", False) 
        self.destroy()
