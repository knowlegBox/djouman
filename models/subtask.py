from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class SubTask(Base):
    __tablename__ = 'subtasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True) # Duration in minutes
    
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    task = relationship("Task", back_populates="subtasks")
