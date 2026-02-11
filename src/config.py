import os
import json
import logging
from src.constants import CONFIG_FILE, BASE_DIR

logger = logging.getLogger(__name__)

class AppConfig:
    
    def __init__(self):
        self.settings = {
            "language": "pt_BR",
            "first_run": True,
            "loopback_device_guid": None,
            "mic_device_guid": None,
            "output_folder": None
        }
        self.load()
        
    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f: 
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
            
    def save(self):
        try:
            os.makedirs(BASE_DIR, exist_ok=True)
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Config saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
        
    def get(self, key):
        return self.settings.get(key)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save()
