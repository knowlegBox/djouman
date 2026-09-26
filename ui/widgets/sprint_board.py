from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QListWidget, QListWidgetItem, QAbstractItemView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class DraggableTaskList(QListWidget):
    """Liste permettant le glisser-déposer de tâches"""
    task_moved = Signal(int, bool) # task_id, is_now_in_sprint
    
    def __init__(self, is_sprint_list=False):
        super().__init__()
        self.is_sprint_list = is_sprint_list
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            super().dragEnterEvent(event)
            
    def dropEvent(self, event):
        super().dropEvent(event)
        # Notify after drop
        if event.source() != self:
            item = self.currentItem()
            if item:
                task_id = item.data(Qt.UserRole)
                self.task_moved.emit(task_id, self.is_sprint_list)

class SprintBoardTab(QWidget):
    """Onglet affichant le Backlog et le Sprint actuel"""
    
    def __init__(self, task_service, project_service):
        super().__init__()
        self.task_service = task_service
        self.project_service = project_service
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("🏃 Planification du Sprint")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4edea3;")
        header_layout.addWidget(title)
        
        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        layout.addLayout(header_layout)
        
        layout.addSpacing(20)
        
        # Colonnes
        board_layout = QHBoxLayout()
        
        # Backlog
        backlog_layout = QVBoxLayout()
        backlog_title = QLabel("📦 Backlog (À faire plus tard)")
        backlog_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        backlog_layout.addWidget(backlog_title)
        
        self.backlog_list = DraggableTaskList(is_sprint_list=False)
        self.backlog_list.task_moved.connect(self.on_task_moved)
        backlog_layout.addWidget(self.backlog_list)
        
        board_layout.addLayout(backlog_layout)
        
        # Boutons centraux
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        self.move_right_btn = QPushButton("▶️ Ajouter au Sprint")
        self.move_right_btn.clicked.connect(self.move_to_sprint)
        btn_layout.addWidget(self.move_right_btn)
        
        self.move_left_btn = QPushButton("◀️ Retirer du Sprint")
        self.move_left_btn.clicked.connect(self.move_to_backlog)
        btn_layout.addWidget(self.move_left_btn)
        
        board_layout.addLayout(btn_layout)
        
        # Sprint
        sprint_layout = QVBoxLayout()
        sprint_title = QLabel("🔥 Sprint Actuel (Cette semaine)")
        sprint_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
        sprint_layout.addWidget(sprint_title)
        
        self.sprint_list = DraggableTaskList(is_sprint_list=True)
        self.sprint_list.task_moved.connect(self.on_task_moved)
        sprint_layout.addWidget(self.sprint_list)
        
        board_layout.addLayout(sprint_layout)
        
        layout.addLayout(board_layout)
        
    def refresh_data(self):
        self.backlog_list.clear()
        self.sprint_list.clear()
        
        tasks = self.task_service.get_all_tasks()
        
        for task in tasks:
            if task.status == 'completed':
                continue
                
            project_name = f"[{task.project.name}] " if task.project else ""
            item = QListWidgetItem(f"{project_name}{task.title}")
            item.setData(Qt.UserRole, task.id)
            
            if task.in_sprint:
                self.sprint_list.addItem(item)
            else:
                self.backlog_list.addItem(item)
                
    def on_task_moved(self, task_id, is_now_in_sprint):
        self.task_service.update_task(task_id, in_sprint=is_now_in_sprint)
        self.refresh_data()
        
    def move_to_sprint(self):
        item = self.backlog_list.currentItem()
        if item:
            task_id = item.data(Qt.UserRole)
            self.task_service.update_task(task_id, in_sprint=True)
            self.refresh_data()
            
    def move_to_backlog(self):
        item = self.sprint_list.currentItem()
        if item:
            task_id = item.data(Qt.UserRole)
            self.task_service.update_task(task_id, in_sprint=False)
            self.refresh_data()
