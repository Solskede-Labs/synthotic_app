import tkinter as tk
import webbrowser
from src.constants import (
    THEME_COLORS, LANG_TEXTS, DEV_NAME, MY_LINKEDIN, MY_GITHUB, 
    APP_NAME, VERSION, BUILD_DATE, WEBSITE_URL, COPYRIGHT
)
from src.utils import get_resource_path

class AboutWindow(tk.Toplevel):
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.cfg = config
        self.title("About")
        try:
            self.iconbitmap(get_resource_path("app.ico"))
        except Exception:
            pass

        self.geometry("450x550")
        self.configure(bg=THEME_COLORS["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (450/2)
        y = (screen_height/2) - (550/2)
        self.geometry(f'+{int(x)}+{int(y)}')
        
        self.setup_ui()

    def get_text(self, key):
        lang = self.cfg.get("language")
        return LANG_TEXTS.get(lang, LANG_TEXTS["en_US"]).get(key, key)

    def setup_ui(self):
        header = tk.Frame(self, bg=THEME_COLORS["surface"], height=100)
        header.pack(fill="x")
        tk.Label(header, text=APP_NAME.upper(), font=("Segoe UI", 24, "bold"), bg=THEME_COLORS["surface"], fg="white").pack(pady=(25, 5))
        tk.Label(header, text=VERSION, font=("Segoe UI", 10), bg=THEME_COLORS["surface"], fg=THEME_COLORS["primary"]).pack(pady=0)
        
        body_frm = tk.Frame(self, bg=THEME_COLORS["bg"])
        body_frm.pack(fill="both", expand=True, padx=40, pady=30)
        
        tk.Label(body_frm, text=self.get_text("about_desc"), font=("Segoe UI", 11), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text"], justify="center", wraplength=380).pack(pady=10)
        
        tk.Label(body_frm, text=f"Build Date: {BUILD_DATE}", font=("Segoe UI", 9), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"]).pack(pady=(10, 5))
        
        tk.Frame(body_frm, height=1, bg=THEME_COLORS["secondary"], width=300).pack(pady=15)

        tk.Label(body_frm, text="Developed by", font=("Segoe UI", 9), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"]).pack()
        tk.Label(body_frm, text=DEV_NAME, font=("Segoe UI", 11, "bold"), bg=THEME_COLORS["bg"], fg="white").pack(pady=(0, 10))
        
        lbl_web = tk.Label(body_frm, text=WEBSITE_URL, font=("Segoe UI", 10, "underline"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["link"], cursor="hand2")
        lbl_web.pack(pady=5)
        lbl_web.bind("<Button-1>", lambda e: webbrowser.open(WEBSITE_URL))
        
        link_frm = tk.Frame(body_frm, bg=THEME_COLORS["bg"])
        link_frm.pack(pady=15)
        
        lbl_link = tk.Label(link_frm, text="LinkedIn", font=("Segoe UI", 10, "underline"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"], cursor="hand2")
        lbl_link.pack(side="left", padx=10)
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open(MY_LINKEDIN))
        
        lbl_git = tk.Label(link_frm, text="GitHub", font=("Segoe UI", 10, "underline"), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"], cursor="hand2")
        lbl_git.pack(side="left", padx=10)
        lbl_git.bind("<Button-1>", lambda e: webbrowser.open(MY_GITHUB))
        
        tk.Label(self, text=COPYRIGHT, font=("Segoe UI", 8), bg=THEME_COLORS["bg"], fg=THEME_COLORS["text_dim"]).pack(side="bottom", pady=10)
        
        btn = tk.Button(self, text="OK", font=("Segoe UI", 10, "bold"), bg=THEME_COLORS["surface"], fg="white",
                        width=15, bd=0, relief="flat", cursor="hand2", command=self.destroy)
        btn.pack(side="bottom", pady=(0, 20))
