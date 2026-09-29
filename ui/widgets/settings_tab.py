from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QCheckBox, QComboBox, QGroupBox, QPushButton, QHBoxLayout,
                               QMessageBox, QLineEdit)
from PySide6.QtCore import Signal

class SettingsTab(QWidget):
    """Onglet de gestion des paramètres"""
    
    # Signal émis quand les paramètres sont sauvegardés
    settings_changed = Signal()

    def __init__(self, settings_service):
        super().__init__()
        self.settings_service = settings_service
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Groupe Apparence
        app_group = QGroupBox("Apparence")
        app_layout = QFormLayout(app_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Mode Sombre (Djuma)", "dark")
        self.theme_combo.addItem("Mode Clair", "light")
        app_layout.addRow("Thème visuel:", self.theme_combo)
        
        self.editor_input = QLineEdit()
        self.editor_input.setPlaceholderText("code, idea, pycharm, notepad...")
        self.editor_input.setToolTip("Commande CLI pour ouvrir le projet (ex: code pour VS Code, idea pour IntelliJ)")
        app_layout.addRow("Éditeur par défaut (CLI):", self.editor_input)

        # Groupe Notifications
        notif_group = QGroupBox("Notifications & Rappels")
        notif_layout = QFormLayout(notif_group)
        
        self.enable_blocker_cb = QCheckBox("Activer l'écran noir de rappel")
        notif_layout.addRow("", self.enable_blocker_cb)
        
        self.snooze_combo = QComboBox()
        self.snooze_combo.addItem("5 minutes", 5)
        self.snooze_combo.addItem("10 minutes", 10)
        self.snooze_combo.addItem("15 minutes", 15)
        self.snooze_combo.addItem("30 minutes", 30)
        notif_layout.addRow("Délai de relance (Snooze):", self.snooze_combo)
        
        # Groupe Tâches
        task_group = QGroupBox("Comportement des Tâches")
        task_layout = QFormLayout(task_group)
        
        self.duration_combo = QComboBox()
        self.duration_combo.addItem("30 minutes", 30)
        self.duration_combo.addItem("1 heure", 60)
        self.duration_combo.addItem("2 heures", 120)
        task_layout.addRow("Durée par défaut:", self.duration_combo)
        
        self.hide_completed_cb = QCheckBox("Masquer les tâches terminées par défaut")
        task_layout.addRow("", self.hide_completed_cb)
        
        # Bouton Sauvegarder
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton("💾 Sauvegarder les paramètres")
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addWidget(app_group)
        layout.addWidget(notif_group)
        layout.addWidget(task_group)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def load_settings(self):
        """Charge les paramètres actuels dans l'interface"""
        self.enable_blocker_cb.setChecked(self.settings_service.get("enable_screen_blocker", True))
        self.hide_completed_cb.setChecked(self.settings_service.get("hide_completed_tasks", False))
        
        snooze_val = self.settings_service.get("snooze_delay_minutes", 5)
        idx = self.snooze_combo.findData(snooze_val)
        if idx >= 0:
            self.snooze_combo.setCurrentIndex(idx)
            
        dur_val = self.settings_service.get("default_duration_minutes", 60)
        idx = self.duration_combo.findData(dur_val)
        if idx >= 0:
            self.duration_combo.setCurrentIndex(idx)
            
        theme_val = self.settings_service.get("theme", "dark")
        idx = self.theme_combo.findData(theme_val)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
            
        self.editor_input.setText(self.settings_service.get("default_editor", "code"))

    def save_settings(self):
        """Sauvegarde les paramètres et notifie l'application"""
        self.settings_service.set("enable_screen_blocker", self.enable_blocker_cb.isChecked())
        self.settings_service.set("hide_completed_tasks", self.hide_completed_cb.isChecked())
        self.settings_service.set("snooze_delay_minutes", self.snooze_combo.currentData())
        self.settings_service.set("default_duration_minutes", self.duration_combo.currentData())
        self.settings_service.set("theme", self.theme_combo.currentData())
        
        editor = self.editor_input.text().strip()
        self.settings_service.set("default_editor", editor if editor else "code")
        
        QMessageBox.information(self, "Succès", "Les paramètres ont été sauvegardés.")
        self.settings_changed.emit()
