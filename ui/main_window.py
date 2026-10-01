"""
Fenêtre principale de l'application Todo List
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLineEdit, QComboBox, QTableView, 
                               QLabel, QGroupBox, QSplitter, QHeaderView,
                               QMessageBox, QMenu, QTabWidget)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, QColor
from datetime import datetime, timedelta
from services import DatabaseService, TaskService, ProjectService, SettingsService, WorkSessionService
from models import Task, Project
from utils import format_duration, format_priority, format_status, get_priority_color, get_status_color
from config.settings import WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, DEFAULT_STYLES
from ui.models.task_table_model import TaskTableModel
from ui.task_dialog import TaskDialog
from ui.project_dialog import ProjectDialog
from ui.widgets.screen_blocker import TaskScreenBlocker
from ui.widgets.settings_tab import SettingsTab
from ui.widgets.task_card import TaskCard


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.settings_service = SettingsService()
        self.db_service = DatabaseService()
        self.task_service = TaskService(self.db_service)
        self.project_service = ProjectService(self.db_service)
        self.work_session_service = WorkSessionService(self.db_service)
        
        self.setup_ui()
        self.load_data()
        self.setup_connections()
        self.apply_styles()
        
        # Initialisation du système de notification
        self.notified_tasks = {}
        self.active_blockers = []
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_due_tasks)
        self.notification_timer.start(10000)  # Toutes les 10 secondes
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Widget central
        from PySide6.QtWidgets import QStackedWidget
        self.global_stack = QStackedWidget()
        self.setCentralWidget(self.global_stack)
        
        main_container = QWidget()
        self.global_stack.addWidget(main_container)
        
        # Layout principal horizontal (Sidebar + Contenu)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Titre Sidebar
        app_title = QLabel("Djuma")
        app_title.setFont(QFont("Inter", 24, QFont.Bold))
        app_title.setObjectName("app_title")
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)
        
        sidebar_layout.addSpacing(20)
        
        # Boutons de navigation
        from PySide6.QtWidgets import QStackedWidget
        self.stacked_widget = QStackedWidget()
        
        self.nav_tasks_btn = QPushButton("📝 Tâches")
        self.nav_sprint_btn = QPushButton("🏃 Sprint & Backlog")
        self.nav_dashboard_btn = QPushButton("📊 Tableau de bord")
        self.nav_gantt_btn = QPushButton("📅 Calendrier")
        self.nav_settings_btn = QPushButton("⚙️ Paramètres")
        
        self.nav_tasks_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.nav_sprint_btn.clicked.connect(self.switch_to_sprint)
        self.nav_settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.nav_dashboard_btn.clicked.connect(self.switch_to_dashboard)
        self.nav_gantt_btn.clicked.connect(self.switch_to_gantt)
        
        sidebar_layout.addWidget(self.nav_tasks_btn)
        sidebar_layout.addWidget(self.nav_sprint_btn)
        sidebar_layout.addWidget(self.nav_dashboard_btn)
        sidebar_layout.addWidget(self.nav_gantt_btn)
        sidebar_layout.addWidget(self.nav_settings_btn)
        
        sidebar_layout.addSpacing(20)
        
        # Action Buttons in Sidebar
        self.add_task_btn = QPushButton("➕ Nouvelle tâche")
        self.add_task_btn.setObjectName("primary_btn")
        self.add_project_btn = QPushButton("📁 Nouveau projet")
        self.add_project_btn.setObjectName("secondary_btn")
        
        sidebar_layout.addWidget(self.add_task_btn)
        sidebar_layout.addWidget(self.add_project_btn)
        
        sidebar_layout.addSpacing(15)
        
        # Section Projets
        self.sidebar_projects_label = QLabel("PROJETS")
        self.sidebar_projects_label.setStyleSheet("color: #888; font-weight: bold; font-size: 11px;")
        sidebar_layout.addWidget(self.sidebar_projects_label)
        
        from PySide6.QtWidgets import QListWidget
        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet("QListWidget { background: transparent; border: none; } QListWidget::item { padding: 5px; }")
        self.projects_list.setToolTip("Double-cliquez pour ouvrir dans l'éditeur par défaut. Clic droit pour choisir.")
        self.projects_list.itemDoubleClicked.connect(self.open_project_in_editor)
        self.projects_list.itemClicked.connect(self.select_project_from_sidebar)
        self.projects_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.projects_list.customContextMenuRequested.connect(self.show_project_context_menu)
        sidebar_layout.addWidget(self.projects_list)
        
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar)
        
        # --- Right Content Area ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top Bar
        topbar = QWidget()
        topbar.setFixedHeight(60)
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        
        self.toggle_sidebar_btn = QPushButton("☰")
        self.toggle_sidebar_btn.setFixedSize(35, 35)
        self.toggle_sidebar_btn.setStyleSheet("font-size: 18px; border: none; background: transparent;")
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        topbar_layout.addWidget(self.toggle_sidebar_btn)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une tâche...")
        self.search_input.setFixedWidth(300)
        
        topbar_layout.addWidget(QLabel("Recherche:"))
        topbar_layout.addWidget(self.search_input)
        topbar_layout.addStretch()
        
        # Timer Widget
        from ui.widgets.timer_widget import TimerWidget
        self.timer_widget = TimerWidget(self.work_session_service)
        topbar_layout.addWidget(self.timer_widget)
        
        topbar_layout.addStretch()
        
        # Filtres (déplacés dans la top bar pour le moment)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "En attente", "En cours", "Bloquée", "Terminée", "Annulée"])
        self.project_filter = QComboBox()
        self.project_filter.addItems(["Toutes les projets"])
        
        self.sprint_filter = QComboBox()
        self.sprint_filter.addItems(["Tous", "Sprint Actuel", "Backlog"])
        
        topbar_layout.addWidget(QLabel("Vue:"))
        topbar_layout.addWidget(self.sprint_filter)
        
        topbar_layout.addWidget(QLabel("Statut:"))
        topbar_layout.addWidget(self.status_filter)
        topbar_layout.addWidget(QLabel("Projet:"))
        topbar_layout.addWidget(self.project_filter)
        
        
        # Toggle Vue
        self.view_toggle_layout = QHBoxLayout()
        self.view_grid_btn = QPushButton("🗂️ Cartes")
        self.view_list_btn = QPushButton("📄 Liste")
        self.view_grid_btn.setObjectName("secondary_btn")
        self.view_list_btn.setObjectName("secondary_btn")
        self.view_toggle_layout.addWidget(self.view_grid_btn)
        self.view_toggle_layout.addWidget(self.view_list_btn)
        topbar_layout.addLayout(self.view_toggle_layout)
        
        self.refresh_btn = QPushButton("🔄 Actualiser")
        topbar_layout.addWidget(self.refresh_btn)
        
        right_layout.addWidget(topbar)
        right_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(right_widget)
        
        # --- View 0: Tâches ---
        tasks_view = QWidget()
        tasks_layout = QVBoxLayout(tasks_view)
        
        from PySide6.QtWidgets import QStackedWidget, QScrollArea, QGridLayout
        
        self.task_view_stack = QStackedWidget()
        
        # --- Page 0: Kanban View ---
        from ui.widgets.kanban_board import KanbanBoard
        self.kanban_board = KanbanBoard()
        self.kanban_board.task_clicked.connect(self.edit_task_from_card)
        self.kanban_board.timer_toggled.connect(self.toggle_task_timer)
        self.task_view_stack.addWidget(self.kanban_board)
        
        # --- Page 1: List View (Tableau) + Details ---
        content_splitter = QSplitter(Qt.Horizontal)
        
        self.task_table = QTableView()
        self.task_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_table.setSelectionBehavior(QTableView.SelectRows)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSortingEnabled(True)
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        self.task_title = QLabel("Sélectionnez une tâche")
        self.task_title.setFont(QFont("Inter", 14, QFont.Bold))
        self.task_description = QLabel("")
        self.task_description.setWordWrap(True)
        self.task_details = QLabel("")
        details_layout.addWidget(self.task_title)
        details_layout.addWidget(self.task_description)
        details_layout.addWidget(self.task_details)
        
        try:
            from PySide6.QtCharts import QChartView
            from PySide6.QtGui import QPainter
            self.chart_view = QChartView()
            self.chart_view.setRenderHint(QPainter.Antialiasing)
            self.chart_view.setMinimumHeight(200)
            details_layout.addWidget(self.chart_view)
        except ImportError:
            self.chart_view = None
            
        
        # Configuration des vues (Cartes par défaut)
        self.task_view_stack.setCurrentIndex(0)
        details_layout.addStretch()
        content_splitter.addWidget(self.task_table)
        content_splitter.addWidget(details_widget)
        content_splitter.setSizes([600, 300])
        
        self.task_view_stack.addWidget(content_splitter)
        
        tasks_layout.addWidget(self.task_view_stack)
        self.stacked_widget.addWidget(tasks_view)
        
        # --- View 1: Paramètres ---
        self.settings_tab = SettingsTab(self.settings_service)
        self.settings_tab.settings_changed.connect(self.on_settings_changed)
        self.stacked_widget.addWidget(self.settings_tab)
        
        # --- View 2: Dashboard ---
        from ui.widgets.dashboard_tab import DashboardTab
        self.dashboard_tab = DashboardTab(self.task_service, self.project_service, self.work_session_service)
        self.stacked_widget.addWidget(self.dashboard_tab)
        
        # --- View 3: Sprint Board ---
        from ui.widgets.sprint_board import SprintBoardTab
        self.sprint_board_tab = SprintBoardTab(self.task_service, self.project_service)
        self.stacked_widget.addWidget(self.sprint_board_tab)
        
        # --- View 4: Gantt Chart ---
        from ui.widgets.gantt_tab import GanttTab
        self.gantt_tab = GanttTab(self.task_service)
        self.gantt_tab.gantt_widget.task_double_clicked.connect(self.edit_task_from_card)
        self.stacked_widget.addWidget(self.gantt_tab)
        
        self.stacked_widget.setCurrentIndex(0)
        
        # --- Focus Mode ---
        from ui.widgets.focus_widget import FocusModeWidget
        self.focus_widget = FocusModeWidget(self.work_session_service, self.task_service)
        self.focus_widget.exit_requested.connect(self.exit_focus_mode)
        self.global_stack.addWidget(self.focus_widget)
        
    def enter_focus_mode(self, task_id):
        """Passe en mode focus plein écran à partir d'un ID de tâche"""
        task = self.task_service.get_task(task_id)
        if not task:
            return
            
        # S'assurer que le timer démarre
        active = self.work_session_service.get_active_session()
        if not active or active.task_id != task.id:
            self.work_session_service.start_session(task.id)
            self.timer_widget.check_active_session()
            
        self.focus_widget.start_focus(task)
        self.global_stack.setCurrentIndex(1)
        self.showFullScreen()
        
    def exit_focus_mode(self):
        """Quitte le mode focus"""
        self.focus_widget.stop_focus()
        self.global_stack.setCurrentIndex(0)
        self.showNormal()
        self.load_data()
        
    def toggle_sidebar(self):
        """Affiche ou masque la barre latérale"""
        self.sidebar.setVisible(not self.sidebar.isVisible())
        
    def select_project_from_sidebar(self, item):
        """Filtre les tâches quand on clique sur un projet dans la liste"""
        project_name = item.data(Qt.UserRole + 1)
        if project_name:
            idx = self.project_filter.findText(project_name)
            if idx >= 0:
                self.project_filter.setCurrentIndex(idx)
                
    def on_settings_changed(self):
        """Callback quand les paramètres sont modifiés"""
        self.apply_styles()
        self.load_data()  # Recharger les tâches si hide_completed_tasks a changé
        self.filter_tasks()
    
    def setup_connections(self):
        """Configure les connexions des signaux"""
        self.add_task_btn.clicked.connect(self.add_task)
        self.add_project_btn.clicked.connect(self.add_project)
        self.refresh_btn.clicked.connect(self.load_data)
        self.view_grid_btn.clicked.connect(lambda: self.task_view_stack.setCurrentIndex(0))
        self.view_list_btn.clicked.connect(lambda: self.task_view_stack.setCurrentIndex(1))
        
        self.timer_widget.focus_requested.connect(self.enter_focus_mode)
        
        self.search_input.textChanged.connect(self.filter_tasks)
        self.sprint_filter.currentTextChanged.connect(self.filter_tasks)
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        self.project_filter.currentTextChanged.connect(self.filter_tasks)
        
        self.task_table.selectionModel().selectionChanged.connect(self.show_task_details)
        self.task_table.customContextMenuRequested.connect(self.show_context_menu)
        self.task_table.doubleClicked.connect(self.edit_task_by_index)
    
    def apply_styles(self):
        """Applique les styles CSS basés sur le thème sélectionné"""
        from config.settings import DARK_THEME, LIGHT_THEME
        theme = self.settings_service.get("theme", "dark")
        
        if theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        else:
            self.setStyleSheet(DARK_THEME)
            
        # Additional dynamic styling based on theme
        if theme == "dark":
            self.sidebar.setStyleSheet("QWidget#sidebar { background-color: #1a211d; border-right: 1px solid #3c4a42; } QLabel#app_title { color: #4edea3; }")
            self.findChild(QWidget, "topbar").setStyleSheet("QWidget#topbar { background-color: #0e1511; border-bottom: 1px solid #3c4a42; }")
        else:
            self.sidebar.setStyleSheet("QWidget#sidebar { background-color: #e9ecef; border-right: 1px solid #dee2e6; } QLabel#app_title { color: #007bff; }")
            self.findChild(QWidget, "topbar").setStyleSheet("QWidget#topbar { background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }")
            
    def load_data(self):
        """Charge les données"""
        self.load_tasks()
        self.load_projects()
        self.filter_tasks()
        
    def switch_to_dashboard(self):
        self.dashboard_tab.refresh_data()
        self.stacked_widget.setCurrentIndex(2)
        
    def switch_to_sprint(self):
        self.sprint_board_tab.refresh_data()
        self.stacked_widget.setCurrentIndex(3)
        
    def switch_to_gantt(self):
        self.stacked_widget.setCurrentIndex(4)
    
    def load_tasks(self):
        """Charge la liste des tâches"""
        tasks = self.task_service.get_all_tasks()
        
        # Créer ou mettre à jour le modèle
        if not hasattr(self, 'task_model'):
            self.task_model = TaskTableModel(tasks)
            self.task_table.setModel(self.task_model)
            
            # Ajustement des colonnes une fois le modèle défini
            header = self.task_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Statut
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Priorité
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Durée
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Projet
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Date échéance
            header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Créée le
        else:
            self.task_model.set_tasks(tasks)
    
    def load_projects(self):
        """Charge la liste des projets"""
        current_project_text = self.project_filter.currentText()
        
        self.project_filter.clear()
        self.project_filter.addItem("Toutes les projets")
        self.projects_list.clear()
        
        from PySide6.QtWidgets import QListWidgetItem
        from PySide6.QtGui import QColor
        
        projects = self.project_service.get_all_projects()
        for project in projects:
            self.project_filter.addItem(f"{project.name}")
            
            # Temps total par projet
            time_sec = self.work_session_service.get_project_total_time(project.id)
            time_str = f" - {time_sec // 3600}h {(time_sec % 3600) // 60}m" if time_sec > 0 else ""
            
            item = QListWidgetItem(f"● {project.name}{time_str}")
            item.setForeground(QColor(project.color or "#4edea3"))
            item.setData(Qt.UserRole, project.local_path)
            item.setData(Qt.UserRole + 1, project.name)
            self.projects_list.addItem(item)
            
        # Restore filter selection
        idx = self.project_filter.findText(current_project_text)
        if idx >= 0:
            self.project_filter.setCurrentIndex(idx)
            
        # Restore sidebar list selection
        for i in range(self.projects_list.count()):
            item = self.projects_list.item(i)
            if item.data(Qt.UserRole + 1) == current_project_text:
                item.setSelected(True)
                break
            
    def open_project_in_editor(self, item, editor_cmd=None):
        """Ouvre le projet sélectionné dans l'éditeur spécifié via subprocess"""
        local_path = item.data(Qt.UserRole)
        if not local_path:
            return
            
        import os
        import subprocess
        import shutil
        from PySide6.QtWidgets import QMessageBox
        
        if not editor_cmd:
            editors_str = self.settings_service.get("default_editor", "code")
            editors = [e.strip() for e in editors_str.split(",") if e.strip()]
            editor_cmd = editors[0] if editors else "code"
            
        if not os.path.exists(local_path):
            QMessageBox.warning(self, "Erreur", "Le dossier du projet n'existe plus à cet emplacement.")
            return

        # Recherche de l'exécutable absolu
        cmd_path = shutil.which(editor_cmd)
        if not cmd_path:
            # Sur Windows, essayer explicitement avec .cmd (pour VS Code) ou .exe
            cmd_path = shutil.which(f"{editor_cmd}.cmd") or shutil.which(f"{editor_cmd}.exe")
            
        if not cmd_path:
            QMessageBox.warning(
                self, 
                "Éditeur introuvable", 
                f"La commande '{editor_cmd}' n'a pas été trouvée sur votre système.\n\n"
                "Assurez-vous que l'éditeur est installé et ajouté à vos variables d'environnement (PATH)."
            )
            return

        try:
            # Utilisation du chemin absolu avec shell=False est beaucoup plus fiable sur Windows
            # On passe simplement le chemin du dossier comme argument
            subprocess.Popen([cmd_path, local_path])
        except Exception as e:
            QMessageBox.warning(self, "Erreur critique", f"Une erreur est survenue lors de l'ouverture : {str(e)}")
    
    def add_task(self):
        """Ouvre le dialogue d'ajout de tâche"""
        dialog = TaskDialog(self.task_service, self.project_service, settings_service=self.settings_service, parent=self)
        if dialog.exec() == TaskDialog.Accepted:
            self.load_data()
    
    def add_project(self):
        """Ouvre le dialogue d'ajout de projet"""
        dialog = ProjectDialog(self.project_service, parent=self)
        if dialog.exec() == ProjectDialog.Accepted:
            self.load_projects()
            
    def show_project_context_menu(self, position):
        """Affiche le menu contextuel pour la liste des projets"""
        item = self.projects_list.itemAt(position)
        if not item:
            return
            
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Modifier le projet", self)
        edit_action.triggered.connect(lambda: self.edit_project_from_sidebar(item))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        editors_str = self.settings_service.get("default_editor", "code")
        editors = [e.strip() for e in editors_str.split(",") if e.strip()]
        if not editors:
            editors = ["code"]
            
        for editor in editors:
            open_action = QAction(f"💻 Ouvrir dans {editor}", self)
            open_action.triggered.connect(lambda checked=False, e=editor, i=item: self.open_project_in_editor(i, e))
            menu.addAction(open_action)
        
        menu.exec(self.projects_list.mapToGlobal(position))
        
    def edit_project_from_sidebar(self, item):
        """Ouvre le dialogue de modification de projet pour le projet sélectionné"""
        project_name = item.data(Qt.UserRole + 1)
        if not project_name:
            return
            
        projects = self.project_service.get_all_projects()
        target_project = next((p for p in projects if p.name == project_name), None)
        
        if target_project:
            dialog = ProjectDialog(self.project_service, project=target_project, parent=self)
            if dialog.exec() == ProjectDialog.Accepted:
                self.load_data()
    
    def edit_task_from_card(self, task):
        """Ouvre la boîte de dialogue pour éditer une tâche depuis la vue carte"""
        dialog = TaskDialog(self.task_service, self.project_service, task, self.settings_service, self)
        if dialog.exec():
            self.load_data()
            
    def toggle_task_timer(self, task):
        """Gère le démarrage/arrêt du chronomètre pour une tâche"""
        active_session = self.work_session_service.get_active_session()
        if active_session and active_session.task_id == task.id:
            self.timer_widget.stop_session()
        else:
            self.timer_widget.start_session(task.id)

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
            if task.project:
                details.append(f"Projet: {task.project.name}")
            if task.start_date:
                details.append(f"Début: {task.start_date.strftime('%d/%m/%Y %H:%M')}")
            if task.end_date:
                details.append(f"Fin: {task.end_date.strftime('%d/%m/%Y %H:%M')}")
            
            self.task_details.setText("\n".join(details))
    
    def filter_tasks(self):
        """Filtre les tâches selon les critères"""
        search_text = self.search_input.text().lower()
        status_text = self.status_filter.currentText()
        project_text = self.project_filter.currentText()
        sprint_text = self.sprint_filter.currentText()
        today = datetime.now().date()
        
        all_tasks = self.task_service.get_all_tasks()
        filtered_tasks = []
        
        hide_completed = getattr(self, 'settings_service', None) and self.settings_service.get("hide_completed_tasks", False)
        
        for task in all_tasks:
            match_sprint = True
            if sprint_text == "Sprint Actuel" and not task.in_sprint:
                match_sprint = False
            elif sprint_text == "Backlog" and task.in_sprint:
                match_sprint = False
                
            # Masquer les tâches terminées par défaut si le paramètre est actif
            if status_text == "Tous" and hide_completed and task.status == 'completed':
                continue
                
            # Filtre de recherche texte (titre ou description)
            match_search = True
            if search_text:
                title = task.title.lower() if task.title else ""
                desc = task.description.lower() if task.description else ""
                if search_text not in title and search_text not in desc:
                    match_search = False
            
            # Filtre de statut
            match_status = True
            if status_text != "Tous":
                if format_status(task.status) != status_text:
                    match_status = False
                    
            # Filtre de projet
            match_project = True
            if project_text != "tous les projets":
                cat_name = task.project.name if task.project else "Aucune"
                if cat_name != project_text:
                    match_project = False
            
            if match_search and match_status and match_project and match_sprint:
                filtered_tasks.append(task)
                
        if hasattr(self, 'task_model'):
            self.task_model.set_tasks(filtered_tasks)
            self.update_chart()
            
        # Mettre à jour la vue Kanban
        if hasattr(self, 'kanban_board'):
            self.kanban_board.set_tasks(filtered_tasks)
            
        # Mettre à jour la vue Gantt
        if hasattr(self, 'gantt_tab'):
            self.gantt_tab.set_tasks(filtered_tasks)
            
    def update_chart(self):
        """Met à jour le graphique des statistiques"""
        if not hasattr(self, 'chart_view') or not self.chart_view:
            return
            
        try:
            from PySide6.QtCharts import QChart, QPieSeries
            from utils import get_status_color
            
            # Calculer les statistiques à partir des tâches actuellement filtrées
            tasks = []
            if hasattr(self, 'task_model'):
                tasks = self.task_model.tasks
                
            total = len(tasks)
            
            if total == 0:
                self.chart_view.setChart(QChart())
                return
                
            pending = sum(1 for t in tasks if t.status == 'pending')
            in_progress = sum(1 for t in tasks if t.status == 'in_progress')
            completed = sum(1 for t in tasks if t.status == 'completed')
            
            series = QPieSeries()
            
            if pending > 0:
                slice_pending = series.append(f"En attente ({pending})", pending)
                slice_pending.setColor(QColor(get_status_color('pending')))
                
            if in_progress > 0:
                slice_progress = series.append(f"En cours ({in_progress})", in_progress)
                slice_progress.setColor(QColor(get_status_color('in_progress')))
                
            if completed > 0:
                slice_completed = series.append(f"Terminée ({completed})", completed)
                slice_completed.setColor(QColor(get_status_color('completed')))
                
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Répartition des tâches affichées")
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.chart_view.setChart(chart)
        except Exception as e:
            print(f"Erreur lors de la mise à jour du graphique: {e}")
            
    def check_due_tasks(self):
        """Vérifie si une tâche a dépassé son échéance et affiche l'écran noir si nécessaire"""
        if not hasattr(self, 'task_model'):
            return
            
        if not self.settings_service.get("enable_screen_blocker", True):
            return
            
        import datetime
        now = datetime.datetime.now()
        
        for task in self.task_service.get_all_tasks():
            if task.status in ['pending', 'in_progress'] and task.start_date:
                if now >= task.start_date:
                    should_notify = False
                    
                    if task.id not in self.notified_tasks:
                        should_notify = True
                    else:
                        last_notified = self.notified_tasks[task.id]
                        # Snooze basé sur les paramètres
                        if now >= last_notified + datetime.timedelta(minutes=5):
                            should_notify = True
                            
                    if should_notify:
                        # Ne pas afficher si un écran pour cette tâche est déjà visible
                        already_shown = any(hasattr(b, 'task') and b.task.id == task.id for b in self.active_blockers)
                        if not already_shown:
                            self.show_task_blocker(task)
                            
    def show_task_blocker(self, task):
        """Affiche l'écran noir pour une tâche"""
        blocker = TaskScreenBlocker(task, self.on_blocker_dismissed)
        self.active_blockers.append(blocker)
        blocker.showFullScreen()
        
    def on_blocker_dismissed(self, task_id):
        """Callback appelé quand l'utilisateur clique sur Quitter"""
        self.notified_tasks[task_id] = datetime.now()
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        indexes = self.task_table.selectionModel().selectedRows()
        if not indexes:
            return
            
        tasks = [self.task_model.get_task(idx.row()) for idx in indexes if self.task_model.get_task(idx.row())]
        if not tasks:
            return
            
        menu = QMenu(self)
        
        if len(tasks) == 1:
            task = tasks[0]
            edit_action = QAction("✏️ Modifier", self)
            edit_action.triggered.connect(lambda checked=False, t=task: self.edit_task(t))
            menu.addAction(edit_action)
            
            status_menu = menu.addMenu("🔄 Changer le statut")
            for status_value, status_label in [('pending', 'En attente'), ('in_progress', 'En cours'), ('completed', 'Terminée'), ('cancelled', 'Annulée')]:
                action = QAction(status_label, self)
                action.triggered.connect(lambda checked=False, t=task, s=status_value: self.change_task_status(t, s))
                status_menu.addAction(action)
                
            delete_action = QAction("🗑️ Supprimer", self)
            delete_action.triggered.connect(lambda checked=False, t=task: self.delete_task(t))
            menu.addAction(delete_action)
        else:
            status_menu = menu.addMenu(f"🔄 Changer le statut ({len(tasks)} tâches)")
            for status_value, status_label in [('pending', 'En attente'), ('in_progress', 'En cours'), ('blocked', 'Bloquée'), ('completed', 'Terminée'), ('cancelled', 'Annulée')]:
                action = QAction(status_label, self)
                action.triggered.connect(lambda checked=False, ts=tasks, s=status_value: self.change_tasks_status(ts, s))
                status_menu.addAction(action)
                
            delete_action = QAction(f"🗑️ Supprimer les {len(tasks)} tâches", self)
            delete_action.triggered.connect(lambda checked=False, ts=tasks: self.delete_tasks(ts))
            menu.addAction(delete_action)
            
        menu.exec(self.task_table.mapToGlobal(position))
    
    def edit_task(self, task):
        """Modifie une tâche"""
        if task:
            dialog = TaskDialog(self.task_service, self.project_service, task, self.settings_service, self)
            if dialog.exec() == TaskDialog.Accepted:
                self.load_data()
                
    def edit_task_by_index(self, index):
        """Modifie une tâche suite à un double-clic dans le tableau"""
        if index.isValid():
            task = self.task_model.get_task(index.row())
            if task:
                self.edit_task(task)
    
    def complete_task(self, task):
        """Marque une tâche comme terminée"""
        if self.task_service.mark_completed(task.id):
            self.load_data()
            QMessageBox.information(self, "Succès", "Tâche marquée comme terminée")

    def change_task_status(self, task, status):
        """Change le statut d'une tâche"""
        if self.task_service.update_task(task.id, status=status):
            self.load_data()
            self.update_chart()
            
    def change_tasks_status(self, tasks, status):
        """Change le statut de plusieurs tâches"""
        for task in tasks:
            self.task_service.update_task(task.id, status=status)
        self.load_data()
        self.update_chart()
        QMessageBox.information(self, "Succès", f"Statut mis à jour pour {len(tasks)} tâches")
    
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
                self.update_chart()
                QMessageBox.information(self, "Succès", "Tâche supprimée")
                
    def delete_tasks(self, tasks):
        """Supprime plusieurs tâches"""
        reply = QMessageBox.question(
            self, "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer ces {len(tasks)} tâches ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for task in tasks:
                self.task_service.delete_task(task.id)
            self.load_tasks()
            self.update_chart()
            QMessageBox.information(self, "Succès", f"{len(tasks)} tâches supprimées")
    
    def closeEvent(self, event):
        """Ferme l'application proprement"""
        self.db_service.close()
        event.accept()
