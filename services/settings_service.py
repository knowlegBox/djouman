import os
import json

class SettingsService:
    """Service de gestion des paramètres utilisateur"""
    
    def __init__(self, config_path="config/user_settings.json"):
        self.config_path = config_path
        self.default_settings = {
            "enable_screen_blocker": True,
            "snooze_delay_minutes": 5,
            "default_duration_minutes": 60,
            "hide_completed_tasks": False,
            "theme": "dark"
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.config_path):
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Fusion avec les valeurs par défaut pour s'assurer que toutes les clés existent
            merged = self.default_settings.copy()
            merged.update(settings)
            return merged
        except Exception as e:
            print(f"Erreur de chargement des paramètres: {e}")
            return self.default_settings.copy()
            
    def save_settings(self, settings=None):
        if settings is not None:
            self.settings = settings
            
        # Créer le dossier config s'il n'existe pas
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Erreur de sauvegarde des paramètres: {e}")
            return False
            
    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
