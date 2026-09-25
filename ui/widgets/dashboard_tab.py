from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class StatCard(QFrame):
    def __init__(self, title, value, color="#3498db"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a211d;
                border: 1px solid #3c4a42;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        layout.addStretch()

class DashboardTab(QWidget):
    """Onglet affichant le tableau de bord et les statistiques de temps"""
    
    def __init__(self, task_service, project_service, work_session_service):
        super().__init__()
        self.task_service = task_service
        self.project_service = project_service
        self.work_session_service = work_session_service
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Inter", 24, QFont.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Grille de stats
        self.stats_layout = QGridLayout()
        layout.addLayout(self.stats_layout)
        
        layout.addStretch()
        
    def refresh_data(self):
        """Met à jour les statistiques"""
        # Nettoyer l'ancien layout
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
            
        tasks = self.task_service.get_all_tasks()
        projects = self.project_service.get_all_projects()
        
        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t.status == 'completed')
        in_progress = sum(1 for t in tasks if t.status == 'in_progress')
        
        total_time_sec = 0
        for p in projects:
            total_time_sec += self.work_session_service.get_project_total_time(p.id)
            
        hours = total_time_sec // 3600
        mins = (total_time_sec % 3600) // 60
        time_str = f"{hours}h {mins}m"
        
        self.stats_layout.addWidget(StatCard("Tâches totales", total_tasks, "#ffffff"), 0, 0)
        self.stats_layout.addWidget(StatCard("Tâches terminées", completed, "#4edea3"), 0, 1)
        self.stats_layout.addWidget(StatCard("Tâches en cours", in_progress, "#3498db"), 0, 2)
        self.stats_layout.addWidget(StatCard("Temps total travaillé", time_str, "#f39c12"), 0, 3)
