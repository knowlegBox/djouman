from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
import webbrowser

class FocusModeWidget(QWidget):
    """Widget de mode plein écran (Focus Mode)"""
    
    exit_requested = Signal()
    
    def __init__(self, work_session_service, task_service):
        super().__init__()
        self.work_session_service = work_session_service
        self.task_service = task_service
        self.active_task = None
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)
        
    def setup_ui(self):
        # Fond sombre plein écran
        self.setStyleSheet("background-color: #0e1511;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Bouton Quitter (Haut droite)
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.exit_btn = QPushButton("❌ Quitter le Focus")
        self.exit_btn.setFixedSize(200, 40)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #555; border-radius: 20px; color: #ccc;
            }
            QPushButton:hover { background-color: #222; color: white; }
        """)
        self.exit_btn.clicked.connect(self.exit_requested.emit)
        top_layout.addWidget(self.exit_btn)
        layout.addLayout(top_layout)
        
        layout.addStretch(1)
        
        # Projet et Titre
        self.project_label = QLabel("")
        self.project_label.setAlignment(Qt.AlignCenter)
        self.project_label.setStyleSheet("color: #4edea3; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(self.project_label)
        
        layout.addSpacing(20)
        
        self.task_title_label = QLabel("Titre de la tâche")
        self.task_title_label.setAlignment(Qt.AlignCenter)
        self.task_title_label.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        self.task_title_label.setWordWrap(True)
        layout.addWidget(self.task_title_label)
        
        layout.addSpacing(50)
        
        # Chronomètre Géant
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #fff; font-family: monospace; font-size: 120px; font-weight: bold;")
        layout.addWidget(self.timer_label)
        
        layout.addSpacing(50)
        
        # Boutons d'action centraux
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.done_btn = QPushButton("✅ Marquer comme terminée")
        self.done_btn.setFixedSize(300, 60)
        self.done_btn.setStyleSheet("""
            QPushButton {
                background-color: #4edea3; color: #000; border-radius: 30px; font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3cb87e; }
        """)
        self.done_btn.clicked.connect(self.mark_done)
        action_layout.addWidget(self.done_btn)
        
        action_layout.addSpacing(20)
        
        self.pause_btn = QPushButton("⏸️ Mettre en pause")
        self.pause_btn.setFixedSize(300, 60)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: #000; border-radius: 30px; font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: #d68910; }
        """)
        self.pause_btn.clicked.connect(self.pause_focus)
        action_layout.addWidget(self.pause_btn)
        
        action_layout.addSpacing(20)
        
        self.lofi_btn = QPushButton("🎧 Lancer Lo-Fi")
        self.lofi_btn.setFixedSize(300, 60)
        self.lofi_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; color: white; border-radius: 30px; font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.lofi_btn.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk"))
        action_layout.addWidget(self.lofi_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch(2)
        
    def start_focus(self, task):
        self.active_task = task
        self.task_title_label.setText(task.title)
        if task.project:
            self.project_label.setText(task.project.name.upper())
        else:
            self.project_label.setText("SANS PROJET")
            
        self.timer.start(1000)
        self.update_timer_display()
        
    def stop_focus(self):
        self.timer.stop()
        self.active_task = None
        
    def update_timer_display(self):
        session = self.work_session_service.get_active_session()
        if session and self.active_task and session.task_id == self.active_task.id:
            from datetime import datetime
            delta = datetime.utcnow() - session.start_time
            seconds = int(delta.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{secs:02d}")
        else:
            # Maybe the timer was stopped externally
            self.timer_label.setText("EN PAUSE")
            
    def mark_done(self):
        if self.active_task:
            self.active_task.status = "completed"
            self.task_service.update_task(self.active_task.id, status="completed")
            self.work_session_service.stop_active_session()
            self.exit_requested.emit()
            
    def pause_focus(self):
        """Demande la raison de la pause et met en pause la tâche"""
        if not self.active_task: return
        
        from PySide6.QtWidgets import QInputDialog
        reason, ok = QInputDialog.getText(self, "Mise en pause", "Raison de la pause (optionnel):")
        if ok:
            # On pourrait enregistrer le motif dans les notes de la session
            active_session = self.work_session_service.get_active_session()
            if active_session:
                active_session.notes = reason if reason else "Pause"
                self.work_session_service.db_service.get_session().commit()
                
            self.work_session_service.stop_active_session()
            self.exit_requested.emit()
