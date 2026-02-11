import os
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.utils import setup_logging
from src.ui.main_window import DashboardApp
from src.config import AppConfig

def main():
    lock_path = os.path.join(os.path.expanduser("~"), "synthotic.lock")
    
    try:
        import ctypes
        myappid = 'Synthotic.App.0.4.4'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            sys.exit()
    try:
        with open(lock_path, 'w') as f:
            f.write("LOCKED")

        setup_logging()
        config = AppConfig()
        
        # ONBOARDING WIZARD - Show before main window if first run
        if config.get("first_run"):  # Default is True in AppConfig
            import tkinter as tk
            from src.ui.onboarding_wizard import OnboardingWizard
            
            # Create temporary root window (hidden)
            temp_root = tk.Tk()
            temp_root.withdraw()
            
            # Show wizard
            wizard = OnboardingWizard(None, config)
            temp_root.wait_window(wizard)
            
            # Check if wizard was completed
            if config.get("first_run"):
                # User closed wizard without completing - exit app
                temp_root.destroy()
                return
            
            temp_root.destroy()
        
        # Main application
        app = DashboardApp(config)
        app.mainloop()
        
    finally:
        if os.path.exists(lock_path): 
            try:
                os.remove(lock_path)
            except Exception:
                pass

if __name__ == "__main__":
    main()
