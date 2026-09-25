from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class WorkSession(Base):
    """Modèle représentant une session de travail sur une tâche"""
    __tablename__ = 'work_sessions'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0) # durée en secondes
    notes = Column(String(500), nullable=True)
    
    # Relations
    task = relationship("Task", back_populates="work_sessions")
