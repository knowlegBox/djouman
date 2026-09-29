"""
Dialogue de gestion des projets
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, 
                               QGroupBox, QColorDialog, QLabel, QDateEdit, QFileDialog, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QColor
import subprocess
import os
from services import ProjectService
from models import Project
from config.settings import CATEGORY_COLORS

class CloneThread(QThread):
    finished_signal = Signal(bool, str, str)

    def __init__(self, repo_url, parent_dir):
        super().__init__()
        self.repo_url = repo_url
        self.parent_dir = parent_dir

    def run(self):
        import re
        try:
            print(f"\n🔄 Démarrage du clonage de {self.repo_url}...")
            print(f"📂 Dossier de destination : {self.parent_dir}")
            
            result = subprocess.run(["git", "clone", self.repo_url], cwd=self.parent_dir, check=True, capture_output=True, text=True)
            match = re.search(r'/([^/]+?)(?:\.git)?$', self.repo_url)
            local_path = ""
            if match:
                repo_name = match.group(1)
                local_path = os.path.join(self.parent_dir, repo_name)
                
            print(f"✅ Clonage réussi avec succès dans : {local_path}")
            self.finished_signal.emit(True, "Succès", local_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur Git lors du clonage : {e.stderr}")
            self.finished_signal.emit(False, f"Erreur Git: {e.stderr}", "")
        except Exception as e:
            print(f"❌ Erreur inattendue lors du clonage : {str(e)}")
            self.finished_signal.emit(False, f"Erreur inattendue: {str(e)}", "")


class ProjectDialog(QDialog):
    """Dialogue pour créer ou modifier un projet"""
    
    def __init__(self, project_service: ProjectService, project: Project = None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.project = project
        
        self.setup_ui()
        
        if project:
            self.load_project_data()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle("Nouveau projet" if not self.project else "Modifier le projet")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_group = QGroupBox("Informations du projet")
        form_layout = QFormLayout(form_group)
        
        # Nom
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du projet")
        form_layout.addRow("Nom *:", self.name_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Repository URL
        self.repo_url_input = QLineEdit()
        self.repo_url_input.setPlaceholderText("https://github.com/user/repo")
        form_layout.addRow("Repository URL:", self.repo_url_input)
        
        # Local Path
        self.local_path_layout = QHBoxLayout()
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("C:/chemin/vers/le/projet")
        self.browse_btn = QPushButton("📁")
        self.browse_btn.setFixedWidth(30)
        self.local_path_layout.addWidget(self.local_path_input)
        self.local_path_layout.addWidget(self.browse_btn)
        form_layout.addRow("Chemin Local:", self.local_path_layout)
        
        # Default Branch
        self.default_branch_input = QLineEdit()
        self.default_branch_input.setPlaceholderText("main")
        form_layout.addRow("Branche par défaut:", self.default_branch_input)
        
        # Tracker URL
        self.tracker_url_input = QLineEdit()
        self.tracker_url_input.setPlaceholderText("https://jira... / github issues...")
        form_layout.addRow("Tracker URL:", self.tracker_url_input)
        
        # Statut
        self.status_combo = QComboBox()
        self.status_combo.addItems(["actif", "archivé", "en pause"])
        form_layout.addRow("Statut:", self.status_combo)
        
        # Dates
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date de début:", self.start_date_input)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate().addDays(30))
        form_layout.addRow("Date de fin:", self.end_date_input)
        
        # Couleur
        self.color_layout = QHBoxLayout()
        self.color_combo = QComboBox()
        for color in CATEGORY_COLORS:
            self.color_combo.addItem(f"● {color}", color)
        self.color_picker_btn = QPushButton("🎨 Choisir")
        self.color_preview = QLabel("●")
        self.color_preview.setStyleSheet(f"color: {CATEGORY_COLORS[0]}; font-size: 20px;")
        
        self.color_layout.addWidget(self.color_combo)
        self.color_layout.addWidget(self.color_picker_btn)
        self.color_layout.addWidget(self.color_preview)
        form_layout.addRow("Couleur:", self.color_layout)
        
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
        self.save_btn.clicked.connect(self.save_project)
        self.cancel_btn.clicked.connect(self.reject)
        self.color_combo.currentTextChanged.connect(self.update_color_preview)
        self.color_picker_btn.clicked.connect(self.pick_color)
        self.repo_url_input.textChanged.connect(self.on_repo_url_changed)
        self.browse_btn.clicked.connect(self.browse_local_path)
    
    def browse_local_path(self):
        """Ouvre un dialogue pour choisir le dossier du projet"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier du projet")
        if directory:
            self.local_path_input.setText(directory)
    
    def on_repo_url_changed(self, url):
        """Remplit automatiquement le nom du projet à partir de l'URL"""
        if not self.name_input.text() and url:
            import re
            match = re.search(r'/([^/]+?)(?:\.git)?$', url.strip())
            if match:
                repo_name = match.group(1)
                self.name_input.setText(repo_name.capitalize())
    
    def load_project_data(self):
        """Charge les données du projet à modifier"""
        if not self.project:
            return
        
        self.name_input.setText(self.project.name)
        self.description_input.setPlainText(self.project.description or "")
        self.repo_url_input.setText(self.project.repo_url or "")
        self.local_path_input.setText(self.project.local_path or "")
        self.default_branch_input.setText(self.project.default_branch or "")
        self.tracker_url_input.setText(self.project.tracker_url or "")
        self.status_combo.setCurrentText(self.project.status)
        
        if self.project.start_date:
            self.start_date_input.setDate(self.project.start_date.date())
        if self.project.end_date:
            self.end_date_input.setDate(self.project.end_date.date())
        
        # Couleur
        for i in range(self.color_combo.count()):
            if self.color_combo.itemData(i) == self.project.color:
                self.color_combo.setCurrentIndex(i)
                break
        self.update_color_preview()
    
    def update_color_preview(self):
        """Met à jour l'aperçu de couleur"""
        color = self.color_combo.currentData()
        if color:
            self.color_preview.setStyleSheet(f"color: {color}; font-size: 20px;")
    
    def pick_color(self):
        """Ouvre le sélecteur de couleur"""
        current_color = QColor(self.color_combo.currentData())
        color = QColorDialog.getColor(current_color, self, "Choisir une couleur")
        
        if color.isValid():
            color_hex = color.name()
            if color_hex not in [self.color_combo.itemData(i) for i in range(self.color_combo.count())]:
                self.color_combo.addItem(f"● {color_hex}", color_hex)
            
            for i in range(self.color_combo.count()):
                if self.color_combo.itemData(i) == color_hex:
                    self.color_combo.setCurrentIndex(i)
                    break
    
    def save_project(self):
        """Sauvegarde le projet"""
        name = self.name_input.text().strip()
        if not name:
            self.show_error("Le nom est obligatoire")
            return
        
        repo_url = self.repo_url_input.text().strip()
        local_path = self.local_path_input.text().strip()
        
        # Logique de clonage
        if repo_url and not local_path and not self.project:
            reply = QMessageBox.question(
                self, 
                "Cloner le dépôt ?", 
                "Un lien GitHub a été détecté mais aucun chemin local n'est défini.\nVoulez-vous cloner ce dépôt maintenant ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                parent_dir = QFileDialog.getExistingDirectory(self, "Choisir le dossier parent pour le clone")
                if parent_dir:
                    self.progress = QProgressDialog("Clonage en cours... Veuillez patienter", None, 0, 0, self)
                    self.progress.setWindowTitle("Téléchargement")
                    self.progress.setWindowModality(Qt.WindowModal)
                    self.progress.setCancelButton(None)
                    self.progress.setMinimumDuration(0)  # Force l'affichage immédiat
                    self.progress.show()
                    
                    self.clone_thread = CloneThread(repo_url, parent_dir)
                    self.clone_thread.finished_signal.connect(self.on_clone_finished)
                    self.clone_thread.start()
                    return # Attendre la fin du clonage
        
        self.save_project_data()
        
    def on_clone_finished(self, success, msg, local_path):
        if hasattr(self, 'progress'):
            self.progress.close()
            
        if success:
            self.local_path_input.setText(local_path)
            QMessageBox.information(self, "Succès", f"Dépôt cloné avec succès dans :\n{local_path}")
            self.save_project_data()
        else:
            self.show_error(msg)
            
    def save_project_data(self):
        """Procède à la sauvegarde en base de données"""
        name = self.name_input.text().strip()
        
        if self.project:
            success = self.project_service.update_project(
                self.project.id,
                name=name,
                description=self.description_input.toPlainText().strip(),
                repo_url=self.repo_url_input.text().strip(),
                local_path=self.local_path_input.text().strip(),
                default_branch=self.default_branch_input.text().strip(),
                tracker_url=self.tracker_url_input.text().strip(),
                status=self.status_combo.currentText(),
                color=self.color_combo.currentData(),
                start_date=self.start_date_input.date().toPython(),
                end_date=self.end_date_input.date().toPython()
            )
        else:
            success = self.project_service.create_project(
                name=name,
                description=self.description_input.toPlainText().strip(),
                repo_url=self.repo_url_input.text().strip(),
                local_path=self.local_path_input.text().strip(),
                default_branch=self.default_branch_input.text().strip(),
                tracker_url=self.tracker_url_input.text().strip(),
                status=self.status_combo.currentText(),
                color=self.color_combo.currentData(),
                start_date=self.start_date_input.date().toPython(),
                end_date=self.end_date_input.date().toPython()
            ) is not None
        
        if success:
            self.accept()
        else:
            self.show_error("Erreur lors de la sauvegarde")
    
    def show_error(self, message):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Erreur", message)
