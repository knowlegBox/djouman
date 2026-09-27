"""
Widget Kanban pour afficher les tâches par statut
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from .task_card import TaskCard
from utils import get_status_color

class KanbanColumn(QFrame):
    """Colonne du tableau Kanban"""
    
    def __init__(self, title, status_id, parent=None):
        super().__init__(parent)
        self.title = title
        self.status_id = status_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            KanbanColumn {{
                background-color: transparent;
                border: 1px solid #3c4a42;
                border-radius: 8px;
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        color_indicator = QLabel("●")
        color = get_status_color(self.status_id)
        color_indicator.setStyleSheet(f"color: {color}; font-size: 14px;")
        
        self.count_label = QLabel("(0)")
        self.count_label.setStyleSheet("color: #888; font-size: 12px;")
        
        header_layout.addWidget(color_indicator)
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
        
        # Line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3c4a42;")
        self.layout.addWidget(line)
        
        # Scroll area for cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()
        
        self.scroll_area.setWidget(self.cards_widget)
        self.layout.addWidget(self.scroll_area)
        
    def add_card(self, card):
        # Insert before the stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
    def clear(self):
        # Remove all widgets except the stretch
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
    def update_count(self, count):
        self.count_label.setText(f"({count})")


class KanbanBoard(QWidget):
    """Tableau Kanban complet"""
    
    task_clicked = Signal(object)
    timer_toggled = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.board_scroll = QScrollArea()
        self.board_scroll.setWidgetResizable(True)
        self.board_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.board_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.board_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        self.columns = {
            'pending': KanbanColumn("Backlog", 'pending'),
            'in_progress': KanbanColumn("En cours", 'in_progress'),
            'blocked': KanbanColumn("Bloqué", 'blocked'),
            'completed': KanbanColumn("Terminé", 'completed')
        }
        
        for col_id in ['pending', 'in_progress', 'blocked', 'completed']:
            self.columns[col_id].setMinimumWidth(300)
            self.layout.addWidget(self.columns[col_id])
            
        self.board_scroll.setWidget(self.container)
        main_layout.addWidget(self.board_scroll)
            
    def set_tasks(self, tasks):
        for col in self.columns.values():
            col.clear()
            
        counts = {k: 0 for k in self.columns.keys()}
            
        for task in tasks:
            status = 'blocked' if getattr(task, 'is_blocked', False) else task.status
            if status not in self.columns and status == 'cancelled':
                status = 'blocked' # Map cancelled to blocked or ignore
            
            # Map status
            if status not in self.columns:
                status = 'pending'
                
            card = TaskCard(task)
            card.clicked.connect(lambda t=task: self.task_clicked.emit(t))
            card.double_clicked.connect(lambda t=task: self.task_clicked.emit(t))
            card.timer_toggled.connect(lambda t=task: self.timer_toggled.emit(t))
            
            self.columns[status].add_card(card)
            counts[status] += 1
            
        for status, count in counts.items():
            self.columns[status].update_count(count)
