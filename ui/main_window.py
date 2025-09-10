"""
Fenêtre principale de l'application Todo List
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLineEdit, QComboBox, QTableView, 
                               QLabel, QGroupBox, QSplitter, QHeaderView,
                               QMessageBox, QMenu)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont, QColor
from services import DatabaseService, TaskService, CategoryService
from models import Task, Category
from utils import format_duration, format_priority, format_status, get_priority_color, get_status_color
from config.settings import WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, DEFAULT_STYLES
from ui.models.task_table_model import TaskTableModel
from ui.task_dialog import TaskDialog
from ui.category_dialog import CategoryDialog


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.db_service = DatabaseService()
        self.task_service = TaskService(self.db_service)
        self.category_service = CategoryService(self.db_service)
        
        self.setup_ui()
        self.load_data()
        self.setup_connections()
        self.apply_styles()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Barre d'outils
        toolbar_layout = QHBoxLayout()
        
        # Boutons d'action
        self.add_task_btn = QPushButton("➕ Nouvelle tâche")
        self.add_category_btn = QPushButton("📁 Nouvelle catégorie")
        self.refresh_btn = QPushButton("🔄 Actualiser")
        
        toolbar_layout.addWidget(self.add_task_btn)
        toolbar_layout.addWidget(self.add_category_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addStretch()
        
        # Barre de recherche et filtres
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une tâche...")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "En attente", "En cours", "Terminée", "Annulée"])
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Toutes les catégories"])
        
        search_layout.addWidget(QLabel("Recherche:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Statut:"))
        search_layout.addWidget(self.status_filter)
        search_layout.addWidget(QLabel("Catégorie:"))
        search_layout.addWidget(self.category_filter)
        
        # Zone de contenu principal
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Table des tâches
        self.task_table = QTableView()
        self.task_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_table.setSelectionBehavior(QTableView.SelectRows)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSortingEnabled(True)
        
        # Panneau de détails
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        self.task_title = QLabel("Sélectionnez une tâche")
        self.task_title.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.task_description = QLabel("")
        self.task_description.setWordWrap(True)
        
        self.task_details = QLabel("")
        
        details_layout.addWidget(self.task_title)
        details_layout.addWidget(self.task_description)
        details_layout.addWidget(self.task_details)
        details_layout.addStretch()
        
        content_splitter.addWidget(self.task_table)
        content_splitter.addWidget(details_widget)
        content_splitter.setSizes([600, 300])
        
        # Ajout des éléments au layout principal
        main_layout.addLayout(toolbar_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(content_splitter)
    
    def setup_connections(self):
        """Configure les connexions des signaux"""
        self.add_task_btn.clicked.connect(self.add_task)
        self.add_category_btn.clicked.connect(self.add_category)
        self.refresh_btn.clicked.connect(self.load_data)
        
        self.search_input.textChanged.connect(self.filter_tasks)
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        self.category_filter.currentTextChanged.connect(self.filter_tasks)
        
        self.task_table.selectionModel().selectionChanged.connect(self.show_task_details)
        self.task_table.customContextMenuRequested.connect(self.show_context_menu)
    
    def apply_styles(self):
        """Applique les styles CSS"""
        self.setStyleSheet(DEFAULT_STYLES)
    
    def load_data(self):
        """Charge les données"""
        self.load_tasks()
        self.load_categories()
    
    def load_tasks(self):
        """Charge la liste des tâches"""
        tasks = self.task_service.get_all_tasks()
        
        # Créer ou mettre à jour le modèle
        if not hasattr(self, 'task_model'):
            self.task_model = TaskTableModel(tasks)
            self.task_table.setModel(self.task_model)
        else:
            self.task_model.set_tasks(tasks)
    
    def load_categories(self):
        """Charge la liste des catégories"""
        self.category_filter.clear()
        self.category_filter.addItem("Toutes les catégories")
        
        categories = self.category_service.get_all_categories()
        for category in categories:
            self.category_filter.addItem(f"{category.name}")
    
    def add_task(self):
        """Ouvre le dialogue d'ajout de tâche"""
        dialog = TaskDialog(self.task_service, self.category_service)
        if dialog.exec() == TaskDialog.Accepted:
            self.load_tasks()
    
    def add_category(self):
        """Ouvre le dialogue d'ajout de catégorie"""
        dialog = CategoryDialog(self.category_service)
        if dialog.exec() == CategoryDialog.Accepted:
            self.load_categories()
    
    def show_task_details(self, selection):
        """Affiche les détails de la tâche sélectionnée"""
        if not selection.indexes():
            return
            
        row = selection.indexes()[0].row()
        task = self.task_model.get_task(row)
        
        if task:
            self.task_title.setText(task.title)
            self.task_description.setText(task.description or "Aucune description")
            
            details = []
            details.append(f"Statut: {format_status(task.status)}")
            details.append(f"Priorité: {format_priority(task.priority)}")
            if task.duration:
                details.append(f"Durée: {format_duration(task.duration)}")
            if task.category:
                details.append(f"Catégorie: {task.category.name}")
            if task.due_date:
                details.append(f"Échéance: {task.due_date.strftime('%d/%m/%Y %H:%M')}")
            
            self.task_details.setText("\n".join(details))
    
    def filter_tasks(self):
        """Filtre les tâches selon les critères"""
        # Implémentation du filtrage
        pass
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        index = self.task_table.indexAt(position)
        if not index.isValid():
            return
        
        task = self.task_model.get_task(index.row())
        if not task:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Modifier", self)
        edit_action.triggered.connect(lambda: self.edit_task(task))
        menu.addAction(edit_action)
        
        complete_action = QAction("✅ Terminer", self)
        complete_action.triggered.connect(lambda: self.complete_task(task))
        menu.addAction(complete_action)
        
        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_task(task))
        menu.addAction(delete_action)
        
        menu.exec(self.task_table.mapToGlobal(position))
    
    def edit_task(self, task):
        """Modifie une tâche"""
        if task:
            dialog = TaskDialog(self.task_service, self.category_service, task)
            if dialog.exec() == TaskDialog.Accepted:
                self.load_tasks()
    
    def complete_task(self, task):
        """Marque une tâche comme terminée"""
        if self.task_service.mark_completed(task.id):
            self.load_tasks()
            QMessageBox.information(self, "Succès", "Tâche marquée comme terminée")
    
    def delete_task(self, task):
        """Supprime une tâche"""
        reply = QMessageBox.question(
            self, "Confirmation", 
            "Êtes-vous sûr de vouloir supprimer cette tâche ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.task_service.delete_task(task.id):
                self.load_tasks()
                QMessageBox.information(self, "Succès", "Tâche supprimée")
    
    def closeEvent(self, event):
        """Ferme l'application proprement"""
        self.db_service.close()
        event.accept()
