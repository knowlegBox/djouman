from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from utils import get_priority_color, format_priority, format_status

class TaskCard(QFrame):
    """Widget personnalisé représentant une tâche sous forme de carte"""
    
    # Signaux
    clicked = Signal(object)  # Émet l'objet Task
    double_clicked = Signal(object) # Émet l'objet Task pour édition
    timer_toggled = Signal(object) # Émet l'objet Task pour démarrer/arrêter le timer
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("taskCard")
        # Suppression de la hauteur fixe pour que la carte s'ajuste à son contenu
        self.setup_ui()
        self.update_style()
    def setup_ui(self):
        # Layout principal de la carte ultra-compacte
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Ligne 1 : Titre et Status
        top_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.task.title)
        self.title_label.setFont(QFont("Inter", 10, QFont.Bold))
        self.title_label.setWordWrap(True)
        top_layout.addWidget(self.title_label)
        
        top_layout.addStretch()
        
        self.status_label = QLabel(format_status(self.task.status))
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Geist", 8))
        top_layout.addWidget(self.status_label)
        
        layout.addLayout(top_layout)
        
        # Ligne 2 : Projet, Niveau, et Timer
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Projet (cercle vide)
        cat_name = self.task.project.name if self.task.project else "Sans projet"
        cat_color = self.task.project.color if self.task.project else "#86948a"
        
        self.cat_dot = QLabel("○")
        self.cat_dot.setStyleSheet(f"color: {cat_color}; font-size: 14px; font-weight: bold;")
        
        self.cat_label = QLabel(cat_name)
        self.cat_label.setObjectName("footerLabel")
        self.cat_label.setFont(QFont("Inter", 8))
        
        bottom_layout.addWidget(self.cat_dot)
        bottom_layout.addWidget(self.cat_label)
        
        # Espace
        bottom_layout.addSpacing(5)
        
        # Niveau (Priorité)
        self.priority_badge = QLabel(format_priority(self.task.priority).upper())
        self.priority_badge.setObjectName("priorityBadge")
        self.priority_badge.setFont(QFont("Geist", 8, QFont.Bold))
        self.priority_badge.setContentsMargins(4, 2, 4, 2)
        bottom_layout.addWidget(self.priority_badge)
        
        bottom_layout.addStretch()
        
        # Heure
        if hasattr(self.task, 'start_date') and self.task.start_date:
            time_str = self.task.start_date.strftime("%H:%M")
            self.time_label = QLabel(f"⏱ {time_str}")
            self.time_label.setObjectName("footerLabel")
            self.time_label.setFont(QFont("Geist", 8))
            bottom_layout.addWidget(self.time_label)
            bottom_layout.addSpacing(5)
        
        # Bouton Timer (plus petit)
        from PySide6.QtWidgets import QPushButton
        self.timer_btn = QPushButton("▶️")
        self.timer_btn.setFixedSize(20, 20)
        self.timer_btn.setToolTip("Démarrer le chronomètre")
        self.timer_btn.setStyleSheet("""
            QPushButton { background-color: transparent; border: 1px solid #3c4a42; border-radius: 10px; font-size: 8px;}
            QPushButton:hover { background-color: #242c27; border-color: #4edea3; }
        """)
        self.timer_btn.clicked.connect(self.on_timer_clicked)
        bottom_layout.addWidget(self.timer_btn)
        
        layout.addLayout(bottom_layout)
        
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
            
    def on_timer_clicked(self):
        # On ne propage pas le clic à la carte
        self.timer_toggled.emit(self.task)
