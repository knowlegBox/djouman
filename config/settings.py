"""
Configuration de l'application Todo List
"""
import os
import sys
import shutil
from pathlib import Path

# Chemins de l'application
APP_DIR = Path(__file__).parent.parent
ASSETS_DIR = APP_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

# Emplacement utilisateur sécurisé pour les données (AppData sous Windows)
if sys.platform == "win32":
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "Djuma"
else:
    DATA_DIR = Path.home() / ".djuma"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "todo.db"
SETTINGS_PATH = DATA_DIR / "user_settings.json"

# Migration si un fichier todo.db existait dans le dossier de l'application
LOCAL_DB = APP_DIR / "todo.db"
if LOCAL_DB.exists() and not DB_PATH.exists():
    try:
        shutil.copy2(LOCAL_DB, DB_PATH)
    except Exception:
        pass

# Migration si un fichier user_settings.json existait dans config/
LOCAL_SETTINGS = APP_DIR / "config" / "user_settings.json"
if LOCAL_SETTINGS.exists() and not SETTINGS_PATH.exists():
    try:
        shutil.copy2(LOCAL_SETTINGS, SETTINGS_PATH)
    except Exception:
        pass

# Configuration de la base de données (chemin absolu)
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Configuration de l'interface
WINDOW_TITLE = "Todo List Manager"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800

# Configuration des tâches
DEFAULT_PRIORITY = 1
PRIORITY_LEVELS = {
    1: "Faible",
    2: "Moyen", 
    3: "Élevé"
}

STATUS_OPTIONS = {
    'pending': "En attente",
    'in_progress': "En cours",
    'blocked': "Bloquée",
    'completed': "Terminée",
    'cancelled': "Annulée"
}

# Configuration des catégories
DEFAULT_CATEGORY_COLOR = "#3498db"
CATEGORY_COLORS = [
    "#e74c3c",  # Rouge
    "#3498db",  # Bleu
    "#2ecc71",  # Vert
    "#f39c12",  # Orange
    "#9b59b6",  # Violet
    "#1abc9c",  # Turquoise
    "#34495e",  # Gris foncé
    "#e67e22"   # Orange foncé
]

# Configuration des icônes
ICON_MAPPING = {
    'briefcase': '💼',
    'user': '👤',
    'home': '🏠',
    'heart': '❤️',
    'gamepad': '🎮',
    'book': '📚',
    'car': '🚗',
    'shopping': '🛒',
    'star': '⭐',
    'flag': '🏁'
}

# Styles CSS
LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #f8f9fa;
}
QWidget {
    color: #495057;
    font-family: 'Inter', sans-serif;
}
QPushButton {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover { background-color: #0056b3; }
QPushButton:pressed { background-color: #004085; }
QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #dee2e6;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #007bff; }
QComboBox QAbstractItemView {
    background-color: white;
    color: black;
    selection-background-color: #007bff;
    selection-color: white;
}
QListWidget, QTableView {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    background-color: white;
    alternate-background-color: #f8f9fa;
    gridline-color: #dee2e6;
}
QListWidget::item, QTableView::item { padding: 8px; border-bottom: 1px solid #dee2e6; }
QListWidget::item:selected, QTableView::item:selected { background-color: #007bff; color: white; }
QHeaderView::section {
    background-color: #f8f9fa;
    padding: 4px;
    border: 1px solid #dee2e6;
    font-weight: bold;
}
QGroupBox { font-weight: bold; border: 2px solid #dee2e6; border-radius: 4px; margin-top: 8px; padding-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px; }
"""

DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0e1511;
}
QWidget {
    color: #dde5dd;
    font-family: 'Inter', sans-serif;
}
QPushButton {
    background-color: #4edea3;
    color: #003824;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover { background-color: #0fb981; }
QPushButton:pressed { background-color: #006c49; }
QPushButton#secondary_btn {
    background-color: transparent;
    color: #9ed2b5;
    border: 1px solid #3c4a42;
}
QPushButton#secondary_btn:hover { background-color: #1a211d; }
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {
    border: 1px solid #3c4a42;
    border-radius: 4px;
    padding: 8px;
    background-color: #1a211d;
    color: #dde5dd;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #4edea3;
}
QComboBox QAbstractItemView {
    background-color: white;
    color: black;
    selection-background-color: #4edea3;
    selection-color: black;
}
QListWidget, QTableView {
    border: 1px solid #3c4a42;
    border-radius: 4px;
    background-color: #161d19;
    alternate-background-color: #1a211d;
    gridline-color: #2f3732;
    color: #dde5dd;
}
QListWidget::item, QTableView::item { padding: 8px; border-bottom: 1px solid #2f3732; }
QListWidget::item:selected, QTableView::item:selected { background-color: #242c27; color: #4edea3; border: 1px solid #4edea3;}
QHeaderView::section {
    background-color: #09100c;
    color: #bbcabf;
    padding: 8px;
    border: 1px solid #2f3732;
    font-weight: bold;
}
QGroupBox { font-weight: bold; border: 1px solid #3c4a42; border-radius: 4px; margin-top: 8px; padding-top: 8px; color: #4edea3; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px; }
QScrollBar:vertical {
    background: #09100c;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #2f3732;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

DEFAULT_STYLES = LIGHT_THEME
