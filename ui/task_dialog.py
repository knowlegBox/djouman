"""
Dialogue de création et modification de tâches
"""
import datetime
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
        
        # Dates (Début et Fin)
        from PySide6.QtWidgets import QDateTimeEdit
        from PySide6.QtCore import QDateTime
        
        self.enable_start_date = QCheckBox("Planifier")
        
        dates_layout = QHBoxLayout()
        self.start_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setEnabled(False)
        self.start_date_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        
        self.end_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setEnabled(False)
        self.end_date_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        
        dates_layout.addWidget(QLabel("Début:"))
        dates_layout.addWidget(self.start_date_input)
        dates_layout.addWidget(QLabel("Fin:"))
        dates_layout.addWidget(self.end_date_input)
        
        self.enable_start_date.toggled.connect(self.start_date_input.setEnabled)
        self.enable_start_date.toggled.connect(self.end_date_input.setEnabled)
        
        form_layout.addRow(self.enable_start_date, dates_layout)
        
        # Auto-calcul de la date de fin
        self.duration_input.valueChanged.connect(self.calculate_end_date)
        self.start_date_input.dateTimeChanged.connect(self.calculate_end_date)
        
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
            
        # Onglet Sous-tâches (toujours visible)
        self.subtask_tab = QWidget()
        subtask_layout = QVBoxLayout(self.subtask_tab)
        
        if self.task:
            add_layout = QHBoxLayout()
            self.subtask_input = QLineEdit()
            self.subtask_input.setPlaceholderText("Nouvelle sous-tâche...")
            self.subtask_input.returnPressed.connect(self.add_subtask)
            self.add_subtask_btn = QPushButton("Ajouter")
            add_layout.addWidget(self.subtask_input)
            add_layout.addWidget(self.add_subtask_btn)
            subtask_layout.addLayout(add_layout)

            self.subtask_time_layout = QHBoxLayout()
            self.subtask_start_input = QDateTimeEdit(QDateTime.currentDateTime())
            self.subtask_start_input.setCalendarPopup(True)
            self.subtask_start_input.setDisplayFormat("dd/MM/yyyy HH:mm")
            self.subtask_duration_input = QSpinBox()
            self.subtask_duration_input.setRange(0, 9999)
            self.subtask_duration_input.setSuffix(" min")
            self.subtask_duration_input.setValue(30)
            self.subtask_end_input = QDateTimeEdit(QDateTime.currentDateTime())
            self.subtask_end_input.setCalendarPopup(True)
            self.subtask_end_input.setDisplayFormat("dd/MM/yyyy HH:mm")
            self.subtask_end_input.setEnabled(False)
            self.subtask_time_layout.addWidget(QLabel("Début:"))
            self.subtask_time_layout.addWidget(self.subtask_start_input)
            self.subtask_time_layout.addWidget(QLabel("Durée:"))
            self.subtask_time_layout.addWidget(self.subtask_duration_input)
            self.subtask_time_layout.addWidget(QLabel("Fin:"))
            self.subtask_time_layout.addWidget(self.subtask_end_input)
            self.subtask_start_input.dateTimeChanged.connect(self.calculate_subtask_end_date)
            self.subtask_duration_input.valueChanged.connect(self.calculate_subtask_end_date)
            self.calculate_subtask_end_date()
            subtask_layout.addLayout(self.subtask_time_layout)
            
            self.subtasks_list = QListWidget()
            subtask_layout.addWidget(self.subtasks_list)
            
            self.add_subtask_btn.clicked.connect(self.add_subtask)
            self.subtasks_list.itemChanged.connect(self.subtask_toggled)
        else:
            # Mode création : onglet désactivé avec message
            placeholder_label = QLabel("💡 Sauvegardez d'abord la tâche pour ajouter des sous-tâches.")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("color: #86948a; font-style: italic; padding: 40px;")
            subtask_layout.addStretch()
            subtask_layout.addWidget(placeholder_label)
            subtask_layout.addStretch()
            
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
        
        from PySide6.QtCore import QDateTime
        if hasattr(self.task, 'start_date') and self.task.start_date:
            self.enable_start_date.setChecked(True)
            self.start_date_input.setDateTime(self.task.start_date)
            if hasattr(self.task, 'end_date') and self.task.end_date:
                self.end_date_input.setDateTime(self.task.end_date)
            else:
                self.calculate_end_date()
        
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
            'project_id': self.project_combo.currentData(),
            'start_date': self.start_date_input.dateTime().toPython() if self.enable_start_date.isChecked() else None,
            'end_date': self.end_date_input.dateTime().toPython() if self.enable_start_date.isChecked() else None
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
        """Charge les sous-tâches dans la liste avec bouton × de suppression"""
        if not self.task: return
        self.subtasks_list.blockSignals(True)
        self.subtasks_list.clear()
        
        # S'assurer d'avoir les données fraîches
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        subtasks = session.query(SubTask).filter(SubTask.task_id == self.task.id).order_by(SubTask.id.asc()).all()
        
        from PySide6.QtWidgets import QListWidgetItem, QPushButton as QPB
        from PySide6.QtCore import Qt, QSize
        from functools import partial
        for st in subtasks:
            item = QListWidgetItem()
            start_text = st.start_date.strftime("%d/%m/%Y %H:%M") if st.start_date else "—"
            end_text = st.end_date.strftime("%d/%m/%Y %H:%M") if st.end_date else "—"
            duration_text = f"{st.duration} min" if st.duration is not None else ""
            item_text = f"{st.title}  [{start_text} → {end_text}]"
            if duration_text:
                item_text += f"  ({duration_text})"
            item.setText(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if st.is_completed else Qt.Unchecked)
            item.setData(Qt.UserRole, st.id)
            # Réserver de l'espace pour le bouton ×
            item.setSizeHint(QSize(0, 28))
            self.subtasks_list.addItem(item)
            
            # Bouton × de suppression
            del_btn = QPB("×")
            del_btn.setFixedSize(22, 22)
            del_btn.setToolTip("Supprimer cette sous-tâche")
            del_btn.setStyleSheet("""
                QPushButton { background: transparent; color: #e74c3c; border: none; font-size: 14px; font-weight: bold; }
                QPushButton:hover { background: rgba(231, 76, 60, 0.15); border-radius: 4px; }
            """)
            del_btn.clicked.connect(partial(self.delete_subtask, st.id, st.title))
            
            # Aligner le bouton à droite via un widget wrapper
            from PySide6.QtWidgets import QWidget, QHBoxLayout
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(0, 0, 4, 0)
            wrapper_layout.addStretch()
            wrapper_layout.addWidget(del_btn)
            self.subtasks_list.setItemWidget(item, wrapper)
            
        self.subtasks_list.blockSignals(False)
        session.close()

    def calculate_subtask_end_date(self):
        """Calcule automatiquement la date de fin de la sous-tâche."""
        start_dt = self.subtask_start_input.dateTime().toPython()
        duration_minutes = self.subtask_duration_input.value()
        end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
        self.subtask_end_input.blockSignals(True)
        self.subtask_end_input.setDateTime(end_dt)
        self.subtask_end_input.blockSignals(False)

    def add_subtask(self):
        """Ajoute une sous-tâche et synchronise vers le JSON"""
        title = self.subtask_input.text().strip()
        if not title or not self.task: return
        
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        st = SubTask(title=title, task_id=self.task.id)

        st.start_date = self.subtask_start_input.dateTime().toPython()
        st.duration = self.subtask_duration_input.value()
        st.refresh_end_date()

        session.add(st)
        session.commit()
        session.close()
        
        self.subtask_input.clear()
        self.load_subtasks()
        
        # Sync bidirectionnelle vers le JSON
        self.task_service.sync_subtasks_to_json(self.task.id)

    def subtask_toggled(self, item):
        """Met à jour le statut de la sous-tâche et synchronise vers le JSON"""
        st_id = item.data(Qt.UserRole)
        is_completed = (item.checkState() == Qt.Checked)
        
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        st = session.query(SubTask).filter(SubTask.id == st_id).first()
        if st:
            st.is_completed = is_completed
            session.commit()
        session.close()
        
        # Sync bidirectionnelle vers le JSON
        self.task_service.sync_subtasks_to_json(self.task.id)

    def delete_subtask(self, st_id, st_title):
        """Supprime une sous-tâche après confirmation"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer la sous-tâche « {st_title} » ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        session = self.task_service.db_service.get_session()
        from models.subtask import SubTask
        st = session.query(SubTask).filter(SubTask.id == st_id).first()
        if st:
            session.delete(st)
            session.commit()
        session.close()
        
        self.load_subtasks()
        
        # Sync bidirectionnelle vers le JSON
        self.task_service.sync_subtasks_to_json(self.task.id)

    def calculate_end_date(self):
        """Calcule automatiquement la date de fin en fonction de la date de début et de la durée"""
        if self.duration_input.value() > 0:
            start_dt = self.start_date_input.dateTime()
            # On ajoute la durée en minutes (durée * 60 secondes)
            end_dt = start_dt.addSecs(self.duration_input.value() * 60)
            self.end_date_input.blockSignals(True)
            self.end_date_input.setDateTime(end_dt)
            self.end_date_input.blockSignals(False)

