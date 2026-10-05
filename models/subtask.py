from datetime import timedelta
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

    def refresh_end_date(self):
        """Calcule automatiquement l'heure de fin à partir du début et de la durée."""
        if self.start_date is None:
            return self.end_date

        if self.duration is not None:
            self.end_date = self.start_date + timedelta(minutes=self.duration)
        elif self.end_date is not None and self.start_date is not None:
            self.duration = max(0, int((self.end_date - self.start_date).total_seconds() / 60))

        return self.end_date

    def refresh_duration_from_dates(self):
        """Calcule la durée à partir de la date de début et de fin."""
        if self.start_date is None or self.end_date is None:
            return self.duration

        self.duration = max(0, int((self.end_date - self.start_date).total_seconds() / 60))
        return self.duration
