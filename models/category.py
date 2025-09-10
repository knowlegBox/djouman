"""
Modèle de catégorie pour l'application Todo List
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base


class Category(Base):
    """Modèle pour les catégories de tâches"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7), default="#3498db")  # Code couleur hexadécimal
    icon = Column(String(50))  # Nom de l'icône
    
    # Relations
    tasks = relationship("Task", back_populates="category", lazy="select")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
