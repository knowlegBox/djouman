"""
Widget de liste des tâches
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from models import Task
from ui.widgets.task_item import TaskItemWidget
from utils import format_duration, format_priority, format_status, get_priority_color, get_status_color


class TaskListWidget(QWidget):
    """Widget personnalisé pour afficher la liste des tâches"""
    
    task_selected = Signal(Task)
    task_edit_requested = Signal(Task)
    task_delete_requested = Signal(Task)
    task_complete_requested = Signal(Task)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # En-tête
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Mes Tâches")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Compteur de tâches
        self.count_label = QLabel("0 tâche(s)")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Liste des tâches
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.itemClicked.connect(self.on_task_clicked)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.task_list)
    
    def set_tasks(self, tasks):
        """Met à jour la liste des tâches"""
        self.tasks = tasks
        self.refresh_display()
        self.update_count()
    
    def refresh_display(self):
        """Actualise l'affichage de la liste"""
        self.task_list.clear()
        
        for task in self.tasks:
            item = TaskItemWidget(task)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item.sizeHint())
            list_item.setData(Qt.UserRole, task)
            
            # Couleur selon le statut
            color = get_status_color(task.status)
            list_item.setBackground(QColor(color))
            
            self.task_list.addItem(list_item)
            self.task_list.setItemWidget(list_item, item)
    
    def update_count(self):
        """Met à jour le compteur de tâches"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.status == 'completed')
        self.count_label.setText(f"{completed}/{total} terminée(s)")
    
    def on_task_clicked(self, item):
        """Gère le clic sur une tâche"""
        task = item.data(Qt.UserRole)
        if task:
            self.task_selected.emit(task)
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        item = self.task_list.itemAt(position)
        if not item:
            return
        
        task = item.data(Qt.UserRole)
        if not task:
            return
        
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        
        edit_action = QAction("Modifier", self)
        edit_action.triggered.connect(lambda: self.task_edit_requested.emit(task))
        menu.addAction(edit_action)
        
        if task.status != 'completed':
            complete_action = QAction("Terminer", self)
            complete_action.triggered.connect(lambda: self.task_complete_requested.emit(task))
            menu.addAction(complete_action)
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(lambda: self.task_delete_requested.emit(task))
        menu.addAction(delete_action)
        
        menu.exec(self.task_list.mapToGlobal(position))
