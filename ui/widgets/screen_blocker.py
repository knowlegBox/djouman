from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class TaskScreenBlocker(QWidget):
    """Widget plein écran (noir) pour notifier une tâche"""
    
    def __init__(self, task, on_dismiss_callback):
        super().__init__()
        self.task = task
        self.on_dismiss_callback = on_dismiss_callback
        self.setup_ui()
        
    def setup_ui(self):
        # Configuration pour plein écran, au-dessus de tout, sans bordure
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Titre
        title_label = QLabel(f"Tâche à accomplir :\n{self.task.title}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 48, QFont.Bold))
        title_label.setWordWrap(True)
        
        # Description
        desc_label = QLabel(self.task.description or "Aucune description.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 24))
        desc_label.setWordWrap(True)
        
        # Bouton quitter
        quit_btn = QPushButton("Quitter")
        quit_btn.setFont(QFont("Arial", 20, QFont.Bold))
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
                border-radius: 10px;
                padding: 15px 30px;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        quit_btn.setFixedSize(200, 80)
        quit_btn.clicked.connect(self.dismiss)
        
        # Assemblage
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(50)
        layout.addWidget(desc_label)
        layout.addSpacing(100)
        layout.addWidget(quit_btn, 0, Qt.AlignCenter)
        layout.addStretch()
        
    def dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback(self.task.id)
        self.close()
