"""
Dialogue de gestion des catégories
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, 
                               QGroupBox, QColorDialog, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services import CategoryService
from models import Category
from config.settings import CATEGORY_COLORS, ICON_MAPPING


class CategoryDialog(QDialog):
    """Dialogue pour créer ou modifier une catégorie"""
    
    def __init__(self, category_service: CategoryService, category: Category = None):
        super().__init__()
        self.category_service = category_service
        self.category = category
        
        self.setup_ui()
        
        if category:
            self.load_category_data()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.setWindowTitle("Nouvelle catégorie" if not self.category else "Modifier la catégorie")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Formulaire principal
        form_group = QGroupBox("Informations de la catégorie")
        form_layout = QFormLayout(form_group)
        
        # Nom
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de la catégorie")
        form_layout.addRow("Nom *:", self.name_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description de la catégorie")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
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
        
        # Icône
        self.icon_combo = QComboBox()
        for icon_name, icon_char in ICON_MAPPING.items():
            self.icon_combo.addItem(f"{icon_char} {icon_name}", icon_name)
        form_layout.addRow("Icône:", self.icon_combo)
        
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
        self.save_btn.clicked.connect(self.save_category)
        self.cancel_btn.clicked.connect(self.reject)
        self.color_combo.currentTextChanged.connect(self.update_color_preview)
        self.color_picker_btn.clicked.connect(self.pick_color)
    
    def load_category_data(self):
        """Charge les données de la catégorie à modifier"""
        if not self.category:
            return
        
        self.name_input.setText(self.category.name)
        self.description_input.setPlainText(self.category.description or "")
        
        # Couleur
        for i in range(self.color_combo.count()):
            if self.color_combo.itemData(i) == self.category.color:
                self.color_combo.setCurrentIndex(i)
                break
        
        # Icône
        if self.category.icon:
            for i in range(self.icon_combo.count()):
                if self.icon_combo.itemData(i) == self.category.icon:
                    self.icon_combo.setCurrentIndex(i)
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
            # Ajouter la couleur si elle n'existe pas
            if color_hex not in [self.color_combo.itemData(i) for i in range(self.color_combo.count())]:
                self.color_combo.addItem(f"● {color_hex}", color_hex)
            
            # Sélectionner la couleur
            for i in range(self.color_combo.count()):
                if self.color_combo.itemData(i) == color_hex:
                    self.color_combo.setCurrentIndex(i)
                    break
    
    def save_category(self):
        """Sauvegarde la catégorie"""
        name = self.name_input.text().strip()
        if not name:
            self.show_error("Le nom est obligatoire")
            return
        
        description = self.description_input.toPlainText().strip()
        color = self.color_combo.currentData()
        icon = self.icon_combo.currentData()
        
        if self.category:
            # Modification
            success = self.category_service.update_category(
                self.category.id,
                name=name,
                description=description,
                color=color,
                icon=icon
            )
        else:
            # Création
            success = self.category_service.create_category(
                name=name,
                description=description,
                color=color,
                icon=icon
            ) is not None
        
        if success:
            self.accept()
        else:
            self.show_error("Erreur lors de la sauvegarde")
    
    def show_error(self, message):
        """Affiche un message d'erreur"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Erreur", message)
