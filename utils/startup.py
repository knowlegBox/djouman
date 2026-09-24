"""Configuration du lancement automatique sous Windows."""
import sys
from pathlib import Path


APP_NAME = "Djuma"


def get_startup_command() -> str:
    """Construit la commande utilisée par Windows au démarrage."""
    executable = Path(sys.executable)
    if executable.name.lower() == "python.exe":
        executable = executable.with_name("pythonw.exe")

    main_script = Path(__file__).resolve().parent.parent / "main.py"
    if executable.name.lower() == "pythonw.exe":
        return f'"{executable}" "{main_script}"'
    return f'"{executable}"'


def register_startup() -> bool:
    """Active le lancement automatique pour l'utilisateur Windows courant."""
    if sys.platform != "win32":
        return False

    import winreg

    run_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            run_key_path,
            0,
            winreg.KEY_SET_VALUE,
        ) as run_key:
            winreg.SetValueEx(run_key, APP_NAME, 0, winreg.REG_SZ, get_startup_command())
        return True
    except OSError:
        return False