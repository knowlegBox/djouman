from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class SubTask(Base):
    __tablename__ = 'subtasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    task = relationship("Task", back_populates="subtasks")
