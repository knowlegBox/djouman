"""
Widget de sélection de catégorie
"""
from PySide6.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models import Category
from config.settings import ICON_MAPPING


class CategorySelectorWidget(QWidget):
    """Widget pour sélectionner une catégorie"""
    
    category_changed = Signal(int)  # ID de la catégorie sélectionnée
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QHBoxLayout(self)
        
        # Label
        self.label = QLabel("Catégorie:")
        layout.addWidget(self.label)
        
        # ComboBox
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combo)
        
        # Bouton pour ajouter une catégorie
        self.add_btn = QPushButton("➕")
        self.add_btn.setToolTip("Ajouter une catégorie")
        self.add_btn.clicked.connect(self.add_category_requested)
        layout.addWidget(self.add_btn)
        
        layout.addStretch()
    
    def set_categories(self, categories):
        """Met à jour la liste des catégories"""
        self.categories = categories
        self.refresh_combo()
    
    def refresh_combo(self):
        """Actualise la ComboBox"""
        self.combo.clear()
        self.combo.addItem("Aucune catégorie", None)
        
        for category in self.categories:
            icon = ICON_MAPPING.get(category.icon, "📁")
            text = f"{icon} {category.name}"
            self.combo.addItem(text, category.id)
    
    def get_selected_category_id(self):
        """Retourne l'ID de la catégorie sélectionnée"""
        return self.combo.currentData()
    
    def set_selected_category(self, category_id):
        """Sélectionne une catégorie par son ID"""
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == category_id:
                self.combo.setCurrentIndex(i)
                break
    
    def on_selection_changed(self, index):
        """Gère le changement de sélection"""
        category_id = self.combo.currentData()
        self.category_changed.emit(category_id)
    
    def add_category_requested(self):
        """Émet un signal pour ajouter une catégorie"""
        # Ce signal sera connecté dans le parent
        pass
