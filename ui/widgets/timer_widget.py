from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import QTimer, Qt, Signal
from datetime import datetime

class TimerWidget(QFrame):
    """Widget affichant le chronomètre de la session active"""
    
    focus_requested = Signal(object) # Emit with Task
    
    def __init__(self, work_session_service, parent=None):
        super().__init__(parent)
        self.work_session_service = work_session_service
        self.active_session_start = None
        self.active_task_id = None
        self.active_task_title = None
        self.setup_ui()
        
        # Timer pour mettre à jour l'affichage
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000) # Mise à jour chaque seconde
        
        self.check_active_session()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("timerWidget")
        self.setStyleSheet("""
            QFrame#timerWidget {
                background-color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
            QLabel { color: white; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Icône animée ou statique
        self.icon_label = QLabel("⏱️")
        layout.addWidget(self.icon_label)
        
        # Nom de la tâche
        self.task_label = QLabel("Aucune tâche en cours")
        self.task_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.task_label)
        
        # Chronomètre
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("font-family: monospace; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.time_label)
        
        # Bouton Stop
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.stop_btn.clicked.connect(self.stop_session)
        layout.addWidget(self.stop_btn)
        
        # Bouton Focus
        self.focus_btn = QPushButton("🎯 Focus")
        self.focus_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.focus_btn.clicked.connect(self.request_focus)
        layout.addWidget(self.focus_btn)
        
        self.hide() # Masqué par défaut
        
    def check_active_session(self):
        """Vérifie s'il y a une session active au démarrage"""
        session = self.work_session_service.get_active_session()
        if session and session.task:
            self.active_session_start = session.start_time
            self.active_task_id = session.task.id
            self.active_task_title = session.task.title
            self.task_label.setText(self.active_task_title)
            self.show()
            self.update_display()
        else:
            self.active_session_start = None
            self.active_task_id = None
            self.hide()
            
    def start_session(self, task_id):
        """Démarre une nouvelle session"""
        session = self.work_session_service.start_session(task_id)
        if session and session.task:
            self.active_session_start = session.start_time
            self.active_task_id = session.task.id
            self.active_task_title = session.task.title
            self.task_label.setText(self.active_task_title)
            self.show()
            self.update_display()
            
    def stop_session(self):
        """Arrête la session active"""
        self.work_session_service.stop_active_session()
        self.active_session_start = None
        self.active_task_id = None
        self.hide()
        
    def request_focus(self):
        if self.active_task_id:
            # On demande au parent de lancer le focus en passant l'ID (ou on récupère la tâche fraîchement)
            self.focus_requested.emit(self.active_task_id)
        
    def update_display(self):
        """Met à jour le chronomètre"""
        if self.active_session_start:
            delta = datetime.utcnow() - self.active_session_start
            seconds = int(delta.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{secs:02d}")
