import os
import logging
from PIL import Image, ImageDraw

try:
    import pystray
except ImportError:
    pystray = None

from src.constants import LANG_TEXTS, BASE_DIR, LOG_FILE, VERSION
from src.utils import get_resource_path
from src.platform_utils import open_path

logger = logging.getLogger(__name__)

class TrayManager:
    
    def __init__(self, command_queue, restore_callback, exit_callback, config):
        if pystray is None:
            raise ImportError("pystray not installed")

        self.queue = command_queue
        self.restore_callback = restore_callback
        self.exit_callback = exit_callback
        self.cfg = config
        self.icon = None
        self.is_recording = False
        
    def get_text(self, key):
        lang = self.cfg.get("language")
        return LANG_TEXTS.get(lang, LANG_TEXTS["en_US"]).get(key, key)

    def run(self):
        image = self.create_image("idle")
        self.icon = pystray.Icon("Synthotic", image, f"Synthotic {VERSION}", self.create_menu())
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def update_state(self, state):
        if state == "rec":
            self.is_recording = True
        elif state == "idle":
            self.is_recording = False
            
        if self.icon:
            self.icon.icon = self.create_image(state)
            self.icon.menu = self.create_menu()

    def notify(self, title, message):
        if self.icon:
            self.icon.notify(message, title)

    def create_menu(self):
        items = []
        items.append(pystray.MenuItem(self.get_text("tray_open"), self.restore_callback, default=True))
        items.append(pystray.Menu.SEPARATOR)
        
        if not self.is_recording:
            items.append(pystray.MenuItem(self.get_text("tray_start"), lambda icon, item: self.queue.put(("cmd_start", None))))
            items.append(pystray.MenuItem(self.get_text("tray_import"), lambda icon, item: self.queue.put(("cmd_import", None))))
        else:
            items.append(pystray.MenuItem(self.get_text("tray_stop"), lambda icon, item: self.queue.put(("cmd_stop", None))))
            
        items.append(pystray.Menu.SEPARATOR)
        items.append(pystray.MenuItem(self.get_text("tray_folder"), lambda icon, item: self.safe_open(BASE_DIR)))
        items.append(pystray.MenuItem(self.get_text("tray_logs"), lambda icon, item: self.safe_open(LOG_FILE)))
        items.append(pystray.Menu.SEPARATOR)
        items.append(pystray.MenuItem(self.get_text("tray_about"), lambda icon, item: self.queue.put(("cmd_about", None))))
        items.append(pystray.MenuItem(self.get_text("tray_exit"), self.exit_callback))
        
        return pystray.Menu(*items)

    def create_image(self, state):
        # Try to load app.ico for professional appearance
        try:
            icon_path = get_resource_path("app.ico")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                # Resize to appropriate tray icon size if needed
                if img.size != (64, 64):
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                
                # For recording state, add a red overlay/tint
                if state == "rec":
                    overlay = Image.new('RGBA', img.size, (255, 82, 82, 100))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    img = Image.alpha_composite(img, overlay)
                # For processing state, add a green overlay/tint
                elif state == "proc":
                    overlay = Image.new('RGBA', img.size, (0, 230, 118, 100))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    img = Image.alpha_composite(img, overlay)
                
                return img.convert('RGB')
        except Exception as e:
            logger.debug(f"Could not load app.ico, using fallback: {e}")
        
        # Fallback: draw a simple circle (original behavior)
        color = "#333333"
        if state == "rec": color = "#FF5252"
        elif state == "proc": color = "#00E676"
        
        img = Image.new('RGB', (64, 64), color)
        draw = ImageDraw.Draw(img)
        draw.ellipse((16, 16, 48, 48), fill="white")
        return img
        
    def safe_open(self, path):
        open_path(path)
