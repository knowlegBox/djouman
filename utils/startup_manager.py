import os
import sys
import winreg

class StartupManager:
    """Gestionnaire pour configurer le lancement de l'application au démarrage de Windows."""
    
    APP_NAME = "Djuma"
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @classmethod
    def set_run_on_startup(cls, enable: bool):
        """Active ou désactive le lancement au démarrage."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REGISTRY_KEY, 0, winreg.KEY_ALL_ACCESS)
            
            if enable:
                # Si on est dans un exécutable figé par PyInstaller
                if getattr(sys, 'frozen', False):
                    executable_path = sys.executable
                    command = f'"{executable_path}" --startup'
                else:
                    # En mode développement, on lance via python
                    executable_path = sys.executable
                    script_path = os.path.abspath(sys.argv[0])
                    # Cas spécifique pour lancer depuis main.py ou via un module
                    if not script_path.endswith("main.py"):
                        # Essayer de trouver main.py basé sur le dossier actuel
                        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
                        
                    command = f'"{executable_path}" "{script_path}" --startup'

                winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, cls.APP_NAME)
                except FileNotFoundError:
                    # La clé n'existe pas, rien à supprimer
                    pass
                    
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Erreur lors de la modification du registre de démarrage: {e}")
            return False

    @classmethod
    def is_run_on_startup_enabled(cls) -> bool:
        """Vérifie si l'application est configurée pour se lancer au démarrage."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REGISTRY_KEY, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Erreur lors de la vérification du registre: {e}")
            return False
