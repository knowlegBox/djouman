from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from utils import get_priority_color, format_priority, format_status

class TaskCard(QFrame):
    """Widget personnalisé représentant une tâche sous forme de carte"""
    
    # Signaux
    clicked = Signal(object)  # Émet l'objet Task
    double_clicked = Signal(object) # Émet l'objet Task pour édition
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("taskCard")
        self.setMinimumWidth(280)
        self.setFixedHeight(180)
        self.setup_ui()
        self.update_style()
        
    def setup_ui(self):
        # Layout principal de la carte
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # En-tête : Badge priorité et Menu (virtuel)
        header_layout = QHBoxLayout()
        
        self.priority_badge = QLabel(format_priority(self.task.priority).upper())
        self.priority_badge.setObjectName("priorityBadge")
        self.priority_badge.setFont(QFont("Geist", 9, QFont.Bold))
        self.priority_badge.setContentsMargins(8, 4, 8, 4)
        
        header_layout.addWidget(self.priority_badge)
        header_layout.addStretch()
        
        # Status icône ou texte simple en haut à droite
        self.status_label = QLabel(format_status(self.task.status))
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Geist", 9))
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Titre
        self.title_label = QLabel(self.task.title)
        self.title_label.setFont(QFont("Inter", 12, QFont.Bold))
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        # Description
        desc_text = self.task.description if self.task.description else "Aucune description"
        self.desc_label = QLabel(desc_text)
        self.desc_label.setObjectName("descriptionLabel")
        self.desc_label.setFont(QFont("Inter", 10))
        self.desc_label.setWordWrap(True)
        # Limiter la hauteur pour simuler un line-clamp
        self.desc_label.setMaximumHeight(40) 
        layout.addWidget(self.desc_label)
        
        layout.addStretch()
        
        # Pied de carte : Heure et Catégorie
        footer_layout = QHBoxLayout()
        
        cat_name = self.task.category.name if self.task.category else "Sans catégorie"
        cat_color = self.task.category.color if self.task.category else "#86948a"
        
        self.cat_dot = QLabel("●")
        self.cat_dot.setStyleSheet(f"color: {cat_color}; font-size: 14px;")
        
        self.cat_label = QLabel(cat_name)
        self.cat_label.setObjectName("footerLabel")
        self.cat_label.setFont(QFont("Inter", 9))
        
        footer_layout.addWidget(self.cat_dot)
        footer_layout.addWidget(self.cat_label)
        footer_layout.addStretch()
        
        time_str = ""
        if hasattr(self.task, 'start_date') and self.task.start_date:
            time_str = self.task.start_date.strftime("%H:%M")
        
        self.time_label = QLabel(f"⏱ {time_str}")
        self.time_label.setObjectName("footerLabel")
        self.time_label.setFont(QFont("Geist", 9))
        footer_layout.addWidget(self.time_label)
        
        layout.addLayout(footer_layout)
        
    def update_style(self):
        """Met à jour les styles en fonction de la priorité et du thème"""
        # Obtenir la couleur de base de la priorité
        # priority: 1=Low(Blue/Green), 2=Medium(Orange), 3=High(Red)
        base_color = "#4edea3" # Par défaut
        if self.task.priority == 1:
            base_color = "#3498db" # Bleu clair ou sauge
            bg_badge = "rgba(52, 152, 219, 0.15)"
            color_badge = "#3498db"
        elif self.task.priority == 2:
            base_color = "#f39c12" # Orange
            bg_badge = "rgba(243, 156, 18, 0.15)"
            color_badge = "#f39c12"
        elif self.task.priority == 3:
            base_color = "#e74c3c" # Corail/Rouge
            bg_badge = "rgba(231, 76, 60, 0.15)"
            color_badge = "#e74c3c"
        
        # Récupérer le thème de l'application
        theme = "dark"
        parent = self.parent()
        while parent:
            if hasattr(parent, 'settings_service'):
                theme = parent.settings_service.get('theme', 'dark')
                break
            parent = parent.parent()
            
        bg_card = "#1a211d"
        border_card = "#3c4a42"
        bg_hover = "#242c27"
        text_desc = "#bbcabf"
        
        if theme == "light":
            bg_card = "#ffffff"
            border_card = "#dee2e6"
            bg_hover = "#f8f9fa"
            text_desc = "#6c757d"
        
        # Style spécifique de la carte
        self.setStyleSheet(f"""
            QFrame#taskCard {{
                border-left: 4px solid {base_color};
                border-top: 1px solid {border_card};
                border-right: 1px solid {border_card};
                border-bottom: 1px solid {border_card};
                border-radius: 8px;
                background-color: {bg_card};
            }}
            QFrame#taskCard:hover {{
                border-top: 1px solid #4edea3;
                border-right: 1px solid #4edea3;
                border-bottom: 1px solid #4edea3;
                background-color: {bg_hover};
            }}
            QLabel#priorityBadge {{
                background-color: {bg_badge};
                color: {color_badge};
                border-radius: 4px;
            }}
            QLabel#statusLabel {{
                color: #86948a;
            }}
            QLabel#descriptionLabel {{
                color: {text_desc};
            }}
            QLabel#footerLabel {{
                color: #86948a;
            }}
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task)
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.task)
