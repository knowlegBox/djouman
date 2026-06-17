from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QWidget, QFrame,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon
from typing import List
from models.task import Task
from services.task_service import TaskService


class DailyBriefingDialog(QDialog):
    """Fenêtre affichée au démarrage pour récapituler les tâches du jour"""
    
    # Signal émis lorsque l'utilisateur veut ouvrir l'application principale
    open_main_app = Signal()

    def __init__(self, task_service: TaskService, parent=None):
        super().__init__(parent)
        self.task_service = task_service
        self.tasks = self.task_service.get_tasks_for_today()
        
        self.setup_ui()

    def setup_ui(self):
        # Configuration de la fenêtre principale
        self.setWindowTitle("Djuma - Vos Tâches du Jour")
        self.setFixedSize(600, 700)
        # Supprimer la barre de titre standard pour un look plus moderne
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Le widget principal (pour le style)
        main_widget = QWidget(self)
        main_widget.setObjectName("DailyBriefingMain")
        main_widget.setStyleSheet("""
            QWidget#DailyBriefingMain {
                background-color: #1E1E2E;
                border-radius: 20px;
                border: 1px solid #313244;
            }
        """)
        
        # Ajouter une ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        main_widget.setGraphicsEffect(shadow)
        
        # Layout principal de la fenêtre
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(main_widget)
        window_layout.setContentsMargins(20, 20, 20, 20)
        
        # Layout intérieur
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(25)
        
        # En-tête (Titre et message)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        
        title = QLabel("Bonjour ! 🌞")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #CDD6F4;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle_text = f"Vous avez {len(self.tasks)} tâche(s) prévue(s) pour aujourd'hui." if self.tasks else "Vous n'avez aucune tâche prévue pour aujourd'hui. Profitez de votre journée !"
        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #A6ADC8;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Ligne de séparation
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #313244;")
        layout.addWidget(line)
        
        # Zone de défilement pour les tâches
        if self.tasks:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet("""
                QScrollArea { background: transparent; }
                QScrollBar:vertical {
                    border: none;
                    background: #1E1E2E;
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background: #45475A;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover { background: #585B70; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
            """)
            
            tasks_widget = QWidget()
            tasks_widget.setStyleSheet("background: transparent;")
            tasks_layout = QVBoxLayout(tasks_widget)
            tasks_layout.setSpacing(15)
            tasks_layout.setContentsMargins(0, 0, 10, 0)
            
            for task in self.tasks:
                task_frame = self.create_task_widget(task)
                tasks_layout.addWidget(task_frame)
                
            tasks_layout.addStretch()
            scroll.setWidget(tasks_widget)
            layout.addWidget(scroll, 1)
        else:
            # S'il n'y a pas de tâches, afficher un grand espace vide
            layout.addStretch(1)
            
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        close_btn = QPushButton("Fermer")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #CDD6F4;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45475A; }
            QPushButton:pressed { background-color: #585B70; }
        """)
        close_btn.clicked.connect(self.reject)
        
        open_app_btn = QPushButton("Ouvrir Djuma")
        open_app_btn.setCursor(Qt.PointingHandCursor)
        open_app_btn.setStyleSheet("""
            QPushButton {
                background-color: #89B4FA;
                color: #1E1E2E;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #B4BEFE; }
            QPushButton:pressed { background-color: #74C7EC; }
        """)
        open_app_btn.clicked.connect(self.on_open_app_clicked)
        
        buttons_layout.addWidget(close_btn)
        buttons_layout.addWidget(open_app_btn)
        
        layout.addWidget(line)
        layout.addLayout(buttons_layout)

    def create_task_widget(self, task: Task) -> QFrame:
        """Crée un widget affichant les détails d'une tâche."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border-radius: 12px;
                border: 1px solid #313244;
            }
            QFrame:hover {
                border: 1px solid #89B4FA;
                background-color: #1E1E2E;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Info (Titre et durée/date)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        title_label = QLabel(task.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #CDD6F4; border: none; background: transparent;")
        
        time_text = ""
        if task.start_date:
            time_text = task.start_date.strftime("%H:%M")
            if task.end_date:
                time_text += f" - {task.end_date.strftime('%H:%M')}"
        if task.duration:
            time_text += f" ({task.duration_text})" if time_text else task.duration_text
            
        time_label = QLabel(time_text if time_text else "Pas d'heure spécifiée")
        time_label.setFont(QFont("Segoe UI", 10))
        time_label.setStyleSheet("color: #A6ADC8; border: none; background: transparent;")
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout, 1)
        
        # Catégorie (pastille)
        if task.category:
            cat_label = QLabel(task.category.name)
            cat_label.setStyleSheet(f"""
                color: {task.category.color};
                background-color: {task.category.color}20;
                border: 1px solid {task.category.color}40;
                border-radius: 8px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
            """)
            layout.addWidget(cat_label, 0, Qt.AlignVCenter)
            
        return frame

    def on_open_app_clicked(self):
        """Déclenche le signal et ferme le dialogue."""
        self.open_main_app.emit()
        self.accept()
