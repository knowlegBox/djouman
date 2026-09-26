"""
Modèle de tâche pour l'application Todo List
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Task(Base):
    """Modèle pour les tâches"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(Integer)  # Durée en minutes
    priority = Column(Integer, default=1)  # 1=Faible, 2=Moyen, 3=Élevé
    status = Column(String(20), default='pending')  # pending, in_progress, completed, cancelled
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_type = Column(String(50), default='feature') # bug, feature, refactor, test, doc, hotfix
    branch = Column(String(100))
    ticket_url = Column(String(255))
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(Text)
    effort = Column(String(50))
    effort_description = Column(Text)
    
    project_id = Column(Integer, ForeignKey('projects.id'))
    is_completed = Column(Boolean, default=False)
    in_sprint = Column(Boolean, default=False)
    
    # Relations
    project = relationship("Project", back_populates="tasks", lazy="select")
    work_sessions = relationship("WorkSession", back_populates="task", cascade="all, delete-orphan")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def priority_text(self):
        """Retourne le texte de priorité"""
        priority_map = {1: "Faible", 2: "Moyen", 3: "Élevé"}
        return priority_map.get(self.priority, "Inconnu")
    
    @property
    def status_text(self):
        """Retourne le texte de statut"""
        status_map = {
            'pending': "En attente",
            'in_progress': "En cours",
            'completed': "Terminée",
            'cancelled': "Annulée"
        }
        return status_map.get(self.status, "Inconnu")
    
    @property
    def duration_text(self):
        """Retourne la durée formatée"""
        if not self.duration:
            return "Non définie"
        
        hours = self.duration // 60
        minutes = self.duration % 60
        
        if hours > 0:
            return f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        else:
            return f"{minutes}min"
