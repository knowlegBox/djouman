"""
Dialogue de création et modification de tâches
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QSpinBox, QComboBox, 
                               QDateTimeEdit, QPushButton, QLabel, QGroupBox, QCheckBox,
                               QTabWidget, QListWidget, QWidget)
from PySide6.QtCore import Qt, QDateTime
from services import TaskService, ProjectService
from models import Task
from config.settings import PRIORITY_LEVELS, STATUS_OPTIONS

class TaskDialog(QDialog):
    """Dialogue pour créer ou modifier une tâche"""
    
    def __init__(self, task_service: TaskService, project_service: ProjectService, task=None, settings_service=None, parent=None):
        super().__init__(parent)
        self.task_service = task_service
        self.project_service = project_service
        self.settings_service = settings_service
        self.task = task
        
        self.setup_ui()
        self.load_projects()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle("Nouvelle tâche" if not self.task else "Modifier la tâche")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_group = QGroupBox("Informations de la tâche")
        form_layout = QFormLayout(form_group)
        
        # Titre
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titre de la tâche")
        form_layout.addRow("Titre *:", self.title_input)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["feature", "bug", "refactor", "test", "doc", "hotfix"])
        form_layout.addRow("Type:", self.type_combo)
        
        # Projet
        self.project_combo = QComboBox()
        form_layout.addRow("Projet:", self.project_combo)
        
        # Branche (override projet)
        self.branch_input = QLineEdit()
        self.branch_input.setPlaceholderText("Nom de la branche (ex: feature/123-titre)")
        form_layout.addRow("Branche:", self.branch_input)
        
        # Ticket URL
        self.ticket_input = QLineEdit()
        self.ticket_input.setPlaceholderText("Lien vers le ticket (Jira, GitHub, etc.)")
        form_layout.addRow("Ticket URL:", self.ticket_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description technique ou métier de la tâche")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Effort
        self.effort_combo = QComboBox()
        self.effort_combo.addItems(["XS", "S", "M", "L", "XL"])
        form_layout.addRow("Effort:", self.effort_combo)
        
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
        
        # Bloqué ?
        self.blocked_checkbox = QCheckBox("Tâche bloquée")
        self.blocked_reason = QLineEdit()
        self.blocked_reason.setPlaceholderText("Raison du blocage")
        self.blocked_reason.setEnabled(False)
        self.blocked_checkbox.toggled.connect(self.blocked_reason.setEnabled)
        
        blocked_layout = QHBoxLayout()
        blocked_layout.addWidget(self.blocked_checkbox)
        blocked_layout.addWidget(self.blocked_reason)
        form_layout.addRow("Blocage:", blocked_layout)
        
        # Durée estimée (minutes)
        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 9999)
        self.duration_input.setSuffix(" minutes")
        form_layout.addRow("Durée est.:", self.duration_input)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(form_group, "Détails")
        
        # Onglet Historique Temps
        self.time_tab = QWidget()
        time_layout = QVBoxLayout(self.time_tab)
        
        # En-tête temps total
        self.total_time_label = QLabel("Temps total : 0h 00m 00s")
        self.total_time_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        time_layout.addWidget(self.total_time_label)
        
        # Liste des sessions
        self.sessions_list = QListWidget()
        time_layout.addWidget(QLabel("Historique des sessions :"))
        time_layout.addWidget(self.sessions_list)
        
        if self.task:
            self.tabs.addTab(self.time_tab, "Temps de travail")
            
            # Onglet Sous-tâches
            self.subtask_tab = QWidget()
            subtask_layout = QVBoxLayout(self.subtask_tab)
            
            add_layout = QHBoxLayout()
            self.subtask_input = QLineEdit()
            self.subtask_input.setPlaceholderText("Nouvelle sous-tâche...")
            self.add_subtask_btn = QPushButton("Ajouter")
            add_layout.addWidget(self.subtask_input)
            add_layout.addWidget(self.add_subtask_btn)
            subtask_layout.addLayout(add_layout)
            
            self.subtasks_list = QListWidget()
            subtask_layout.addWidget(self.subtasks_list)
            
            self.add_subtask_btn.clicked.connect(self.add_subtask)
            self.subtasks_list.itemChanged.connect(self.subtask_toggled)
            
            self.tabs.addTab(self.subtask_tab, "Sous-tâches")
            
        layout.addWidget(self.tabs)
        
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
    
    def load_projects(self):
        """Charge les projets disponibles"""
        self.project_combo.clear()
        self.project_combo.addItem("Aucun projet", None)
        
        projects = self.project_service.get_all_projects()
        for project in projects:
            self.project_combo.addItem(project.name, project.id)
    
    def load_task_data(self):
        """Charge les données de la tâche à modifier"""
        if not self.task:
            return
        
        self.title_input.setText(self.task.title)
        self.description_input.setPlainText(self.task.description or "")
        self.type_combo.setCurrentText(self.task.task_type or "feature")
        self.branch_input.setText(self.task.branch or "")
        self.ticket_input.setText(self.task.ticket_url or "")
        
        if self.task.effort:
            self.effort_combo.setCurrentText(self.task.effort)
            
        self.blocked_checkbox.setChecked(self.task.is_blocked)
        if self.task.is_blocked:
            self.blocked_reason.setEnabled(True)
            self.blocked_reason.setText(self.task.blocked_reason or "")
        
        for i in range(self.priority_combo.count()):
            if self.priority_combo.itemData(i) == self.task.priority:
                self.priority_combo.setCurrentIndex(i)
                break
        
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == self.task.status:
                self.status_combo.setCurrentIndex(i)
                break
        
        self.duration_input.setValue(self.task.duration or 0)
        
        if self.task.project_id:
            for i in range(self.project_combo.count()):
                if self.project_combo.itemData(i) == self.task.project_id:
                    self.project_combo.setCurrentIndex(i)
                    break
                    
        # Charger l'historique des temps
        self.load_time_history()
        
        # Charger les sous-tâches
        self.load_subtasks()

    def load_time_history(self):
        """Charge l'historique des sessions de travail"""
        from utils import format_duration
        if not self.task or not hasattr(self.task, 'work_sessions'):
            return
            
        self.sessions_list.clear()
        total_seconds = 0
        
        for session in sorted(self.task.work_sessions, key=lambda s: s.start_time, reverse=True):
            if session.end_time:
                duration_str = format_duration(session.duration // 60) # format_duration expects minutes, or we can make a custom string
                duration_sec = session.duration
                time_str = f"{session.start_time.strftime('%d/%m/%Y %H:%M')} - {duration_sec // 3600}h {(duration_sec % 3600) // 60}m {duration_sec % 60}s"
                total_seconds += duration_sec
            else:
                time_str = f"{session.start_time.strftime('%d/%m/%Y %H:%M')} - EN COURS"
                
            self.sessions_list.addItem(time_str)
            
        # Mettre à jour le temps total
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        time_text = f"Temps total : {hours}h {minutes:02d}m {secs:02d}s"
        
        if self.task.duration:
            est_seconds = self.task.duration * 60
            diff = total_seconds - est_seconds
            diff_hours = abs(diff) // 3600
            diff_mins = (abs(diff) % 3600) // 60
            if diff > 0:
                time_text += f" (Dépassement: +{diff_hours}h {diff_mins:02d}m)"
                self.total_time_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;")
            else:
                time_text += f" (Avance: -{diff_hours}h {diff_mins:02d}m)"
                self.total_time_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #4edea3;")
        else:
            self.total_time_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
        self.total_time_label.setText(time_text)
    
    def save_task(self):
        """Sauvegarde la tâche"""
        title = self.title_input.text().strip()
        if not title:
            self.show_error("Le titre est obligatoire")
            return
        
        duration = self.duration_input.value() if self.duration_input.value() > 0 else None
        
        kwargs = {
            'title': title,
            'description': self.description_input.toPlainText().strip(),
            'task_type': self.type_combo.currentText(),
            'branch': self.branch_input.text().strip(),
            'ticket_url': self.ticket_input.text().strip(),
            'effort': self.effort_combo.currentText(),
            'priority': self.priority_combo.currentData(),
            'status': self.status_combo.currentData(),
            'is_blocked': self.blocked_checkbox.isChecked(),
            'blocked_reason': self.blocked_reason.text().strip() if self.blocked_checkbox.isChecked() else "",
            'duration': duration,
            'project_id': self.project_combo.currentData()
        }
        
        if self.task:
            success = self.task_service.update_task(self.task.id, **kwargs)
        else:
            success = self.task_service.create_task(**kwargs) is not None
        
        if success:
            self.accept()
        else:
            self.show_error("Erreur lors de la sauvegarde")
    
    def show_error(self, message):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Erreur", message)
        
    def load_subtasks(self):
        """Charge les sous-tâches dans la liste"""
        if not self.task: return
        self.subtasks_list.blockSignals(True)
        self.subtasks_list.clear()
        
        # S'assurer d'avoir les données fraîches
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        subtasks = session.query(SubTask).filter(SubTask.task_id == self.task.id).order_by(SubTask.id.asc()).all()
        
        from PySide6.QtWidgets import QListWidgetItem
        from PySide6.QtCore import Qt
        for st in subtasks:
            item = QListWidgetItem(st.title)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if st.is_completed else Qt.Unchecked)
            item.setData(Qt.UserRole, st.id)
            self.subtasks_list.addItem(item)
            
        self.subtasks_list.blockSignals(False)
        session.close()

    def add_subtask(self):
        """Ajoute une sous-tâche"""
        title = self.subtask_input.text().strip()
        if not title or not self.task: return
        
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        st = SubTask(title=title, task_id=self.task.id)
        session.add(st)
        session.commit()
        session.close()
        
        self.subtask_input.clear()
        self.load_subtasks()

    def subtask_toggled(self, item):
        """Met à jour le statut de la sous-tâche"""
        st_id = item.data(Qt.UserRole)
        is_completed = (item.checkState() == Qt.Checked)
        
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        st = session.query(SubTask).filter(SubTask.id == st_id).first()
        if st:
            st.is_completed = is_completed
            session.commit()
        session.close()
