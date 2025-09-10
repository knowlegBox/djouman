"""
Fonctions utilitaires pour l'application Todo List
"""
from datetime import datetime, timedelta
from config.settings import PRIORITY_LEVELS, STATUS_OPTIONS, ICON_MAPPING


def format_duration(minutes: int) -> str:
    """Formate la durée en minutes en texte lisible"""
    if not minutes:
        return "Non définie"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    if hours > 0:
        return f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
    else:
        return f"{minutes}min"


def format_priority(priority: int) -> str:
    """Formate la priorité en texte lisible"""
    return PRIORITY_LEVELS.get(priority, "Inconnue")


def format_status(status: str) -> str:
    """Formate le statut en texte lisible"""
    return STATUS_OPTIONS.get(status, "Inconnu")


def get_icon(icon_name: str) -> str:
    """Retourne l'icône correspondante"""
    return ICON_MAPPING.get(icon_name, "📝")


def format_date(date: datetime) -> str:
    """Formate une date en texte lisible"""
    if not date:
        return "Non définie"
    
    now = datetime.now()
    diff = date - now
    
    if diff.days == 0:
        return "Aujourd'hui"
    elif diff.days == 1:
        return "Demain"
    elif diff.days == -1:
        return "Hier"
    elif diff.days > 0:
        return f"Dans {diff.days} jour(s)"
    else:
        return f"Il y a {abs(diff.days)} jour(s)"


def is_overdue(date: datetime) -> bool:
    """Vérifie si une tâche est en retard"""
    if not date:
        return False
    return date < datetime.now()


def get_priority_color(priority: int) -> str:
    """Retourne la couleur correspondant à la priorité"""
    color_map = {
        1: "#28a745",  # Vert pour faible
        2: "#ffc107",  # Jaune pour moyen
        3: "#dc3545"   # Rouge pour élevé
    }
    return color_map.get(priority, "#6c757d")


def get_status_color(status: str) -> str:
    """Retourne la couleur correspondant au statut"""
    color_map = {
        'pending': "#6c757d",      # Gris
        'in_progress': "#007bff",   # Bleu
        'completed': "#28a745",     # Vert
        'cancelled': "#dc3545"      # Rouge
    }
    return color_map.get(status, "#6c757d")
