"""
Modèle de données pour le TableView des tâches
"""
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor
from models import Task
from utils import format_duration, format_priority, format_status, get_priority_color, get_status_color
from datetime import datetime


class TaskTableModel(QAbstractTableModel):
    """Modèle de données pour afficher les tâches dans un TableView"""
    
    def __init__(self, tasks=None, parent=None):
        super().__init__(parent)
        self.tasks = tasks or []
        self.headers = [
            "Titre",
            "Description", 
            "Statut",
            "Priorité",
            "Durée",
            "Catégorie",
            "Date d'échéance",
            "Créée le"
        ]
    
    def rowCount(self, parent=QModelIndex()):
        """Retourne le nombre de lignes"""
        return len(self.tasks)
    
    def columnCount(self, parent=QModelIndex()):
        """Retourne le nombre de colonnes"""
        return len(self.headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Retourne les données d'en-tête"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        """Retourne les données de la cellule"""
        if not index.isValid():
            return None
        
        task = self.tasks[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:  # Titre
                return task.title
            elif column == 1:  # Description
                return task.description or ""
            elif column == 2:  # Statut
                return format_status(task.status)
            elif column == 3:  # Priorité
                return format_priority(task.priority)
            elif column == 4:  # Durée
                return format_duration(task.duration) if task.duration else "N/A"
            elif column == 5:  # Catégorie
                return task.category.name if task.category else "Aucune"
            elif column == 6:  # Date d'échéance
                return task.due_date.strftime("%d/%m/%Y %H:%M") if task.due_date else "N/A"
            elif column == 7:  # Créée le
                return task.created_at.strftime("%d/%m/%Y %H:%M")
        
        elif role == Qt.BackgroundRole:
            # Couleur de fond selon le statut
            if column == 2:  # Colonne statut
                color = get_status_color(task.status)
                return QColor(color)
            elif column == 3:  # Colonne priorité
                color = get_priority_color(task.priority)
                return QColor(color)
        
        elif role == Qt.TextAlignmentRole:
            if column in [3, 4, 6, 7]:  # Colonnes numériques et dates
                return Qt.AlignCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        
        return None
    
    def set_tasks(self, tasks):
        """Met à jour la liste des tâches"""
        self.beginResetModel()
        self.tasks = tasks
        self.endResetModel()
    
    def get_task(self, row):
        """Retourne la tâche à la ligne spécifiée"""
        if 0 <= row < len(self.tasks):
            return self.tasks[row]
        return None
    
    def flags(self, index):
        """Retourne les flags de la cellule"""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
