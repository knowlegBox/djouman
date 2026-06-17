"""
Widget d'élément de tâche
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from models import Task
from utils import format_duration, format_priority, format_status, get_priority_color, get_status_color


class TaskItemWidget(QWidget):
    """Widget pour afficher un élément de tâche"""
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Icône de statut
        status_icon = self.get_status_icon()
        self.status_label = QLabel(status_icon)
        self.status_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.status_label)
        
        # Informations principales
        info_layout = QVBoxLayout()
        
        # Titre
        self.title_label = QLabel(self.task.title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        # Détails
        details = []
        if self.task.category:
            details.append(f"{self.task.category.name}")
        details.append(f"{format_priority(self.task.priority)}")
        if self.task.duration:
            details.append(f"{format_duration(self.task.duration)}")
        
        if details:
            self.details_label = QLabel(" • ".join(details))
            self.details_label.setFont(QFont("Arial", 9))
            self.details_label.setStyleSheet("color: #666;")
            info_layout.addWidget(self.details_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Badge de statut
        self.status_badge = QLabel(format_status(self.task.status))
        self.status_badge.setStyleSheet(f"""
            background-color: {get_status_color(self.task.status)};
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        """)
        layout.addWidget(self.status_badge)
    
    def get_status_icon(self):
        """Retourne l'icône correspondant au statut"""
        icons = {
            'pending': '',
            'in_progress': '',
            'completed': '',
            'cancelled': ''
        }
        return icons.get(self.task.status, '')
