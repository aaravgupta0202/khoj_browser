import json
import os

class SettingsManager:
    def __init__(self):
        self.settings_file = "browser_settings.json"
        self.default_settings = {
            'appearance': {
                'theme': 'dark',
                'background_type': 'preset',
                'preset_bg': 9,
                'background_color': '#1a1a2e',
                'background_gradient': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        return self.default_settings.copy()
        
    def get(self, section, key, default=None):
        return self.settings.get(section, {}).get(key, default)
        
    def set(self, section, key, value):
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value