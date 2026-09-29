"""
Modèle de projet pour l'application Todo List
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Project(Base):
    """Modèle pour les projets"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    repo_url = Column(String(255))
    local_path = Column(String(500))
    default_branch = Column(String(100))
    tracker_url = Column(String(255))
    color = Column(String(7), default="#3498db")  # Code couleur hexadécimal
    status = Column(String(50), default="actif") # actif, archivé, en pause
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    tasks = relationship("Task", back_populates="project", lazy="select", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
