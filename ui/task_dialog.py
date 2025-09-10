"""
Dialogue de création et modification de tâches
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QSpinBox, QComboBox, 
                               QDateTimeEdit, QPushButton, QLabel, QGroupBox)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
from services import TaskService, CategoryService
from models import Task
from config.settings import PRIORITY_LEVELS, STATUS_OPTIONS


class TaskDialog(QDialog):
    """Dialogue pour créer ou modifier une tâche"""
    
    def __init__(self, task_service: TaskService, category_service: CategoryService, task: Task = None):
        super().__init__()
        self.task_service = task_service
        self.category_service = category_service
        self.task = task
        
        self.setup_ui()
        self.load_categories()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle("Nouvelle tâche" if not self.task else "Modifier la tâche")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_group = QGroupBox("Informations de la tâche")
        form_layout = QFormLayout(form_group)
        
        # Titre
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titre de la tâche")
        form_layout.addRow("Titre *:", self.title_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description de la tâche")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)
        
        # Priorité
        self.priority_combo = QComboBox()
        for priority, text in PRIORITY_LEVELS.items():
            self.priority_combo.addItem(text, priority)
        form_layout.addRow("Priorité:", self.priority_combo)
        
        # Statut
        self.status_combo = QComboBox()
        for status, text in STATUS_OPTIONS.items():
            self.status_combo.addItem(text, status)
        form_layout.addRow("Statut:", self.status_combo)
        
        # Durée
        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 9999)
        self.duration_input.setSuffix(" minutes")
        form_layout.addRow("Durée:", self.duration_input)
        
        # Catégorie
        self.category_combo = QComboBox()
        form_layout.addRow("Catégorie:", self.category_combo)
        
        # Date d'échéance
        self.due_date_input = QDateTimeEdit()
        self.due_date_input.setDateTime(QDateTime.currentDateTime())
        self.due_date_input.setCalendarPopup(True)
        form_layout.addRow("Échéance:", self.due_date_input)
        
        layout.addWidget(form_group)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Enregistrer")
        self.cancel_btn = QPushButton("❌ Annuler")
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connexions
        self.save_btn.clicked.connect(self.save_task)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_categories(self):
        """Charge les catégories disponibles"""
        self.category_combo.clear()
        self.category_combo.addItem("Aucune catégorie", None)
        
        categories = self.category_service.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def load_task_data(self):
        """Charge les données de la tâche à modifier"""
        if not self.task:
            return
        
        self.title_input.setText(self.task.title)
        self.description_input.setPlainText(self.task.description or "")
        
        # Priorité
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == self.task.priority:
                self.priority_combo.setCurrentIndex(i)
                break
        
        # Statut
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == self.task.status:
                self.status_combo.setCurrentIndex(i)
                break
        
        # Durée
        self.duration_input.setValue(self.task.duration or 0)
        
        # Catégorie
        if self.task.category_id:
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.task.category_id:
                    self.category_combo.setCurrentIndex(i)
                    break
        
        # Date d'échéance
        if self.task.due_date:
            self.due_date_input.setDateTime(QDateTime.fromPython(self.task.due_date))
    
    def save_task(self):
        """Sauvegarde la tâche"""
        title = self.title_input.text().strip()
        if not title:
            self.show_error("Le titre est obligatoire")
            return
        
        description = self.description_input.toPlainText().strip()
        priority = self.priority_combo.currentData()
        status = self.status_combo.currentData()
        duration = self.duration_input.value() if self.duration_input.value() > 0 else None
        category_id = self.category_combo.currentData()
        due_date = self.due_date_input.dateTime().toPython()
        
        if self.task:
            # Modification
            success = self.task_service.update_task(
                self.task.id,
                title=title,
                description=description,
                priority=priority,
                status=status,
                duration=duration,
                category_id=category_id,
                due_date=due_date
            )
        else:
            # Création
            success = self.task_service.create_task(
                title=title,
                description=description,
                priority=priority,
                status=status,
                duration=duration,
                category_id=category_id,
                due_date=due_date
            ) is not None
        
        if success:
            self.accept()
        else:
            self.show_error("Erreur lors de la sauvegarde")
    
    def show_error(self, message):
        """Affiche un message d'erreur"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Erreur", message)
