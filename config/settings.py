"""
Configuration de l'application Todo List
"""
import os
from pathlib import Path

# Chemins de l'application
APP_DIR = Path(__file__).parent.parent
ASSETS_DIR = APP_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

# Configuration de la base de données
DATABASE_URL = "sqlite:///todo.db"

# Configuration de l'interface
WINDOW_TITLE = "Todo List Manager"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

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
DEFAULT_STYLES = """
QMainWindow {
    background-color: #f8f9fa;
}

QPushButton {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0056b3;
}

QPushButton:pressed {
    background-color: #004085;
}

QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #dee2e6;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #007bff;
}

QListWidget {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    background-color: white;
    alternate-background-color: #f8f9fa;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #dee2e6;
}

QListWidget::item:selected {
    background-color: #007bff;
    color: white;
}

QLabel {
    color: #495057;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #dee2e6;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px 0 4px;
}
"""
