"""
Service de gestion des tâches
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.task import Task
from .database import DatabaseService


class TaskService:
    """Service de gestion des tâches"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def create_task(self, title: str, description: str = None, duration: int = None, 
                   priority: int = 1, status: str = 'pending', project_id: int = None, 
                   start_date: str = None, end_date: str = None,
                   task_type: str = 'feature', branch: str = None, ticket_url: str = None,
                   is_blocked: bool = False, blocked_reason: str = None,
                   effort: str = None, effort_description: str = None) -> Optional[Task]:
        """Crée une nouvelle tâche"""
        session = self.db_service.get_session()
        try:
            task = Task(
                title=title,
                description=description,
                duration=duration,
                priority=priority,
                status=status,
                project_id=project_id,
                start_date=start_date,
                end_date=end_date,
                task_type=task_type,
                branch=branch,
                ticket_url=ticket_url,
                is_blocked=is_blocked,
                blocked_reason=blocked_reason,
                effort=effort,
                effort_description=effort_description
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la création de la tâche : {e}")
            return None
        finally:
            session.close()
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Récupère une tâche par son ID"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project)).filter(Task.id == task_id).first()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de la tâche : {e}")
            return None
        finally:
            session.close()
    
    def get_all_tasks(self) -> List[Task]:
        """Récupère toutes les tâches"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project)).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []
        finally:
            session.close()
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Récupère les tâches par statut"""
        session = self.db_service.get_session()
        try:
            return session.query(Task).filter(Task.status == status).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []
        finally:
            session.close()
    
    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Récupère les tâches par projet"""
        session = self.db_service.get_session()
        try:
            return session.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []
        finally:
            session.close()
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Met à jour une tâche"""
        session = self.db_service.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la mise à jour de la tâche : {e}")
            return False
        finally:
            session.close()
    
    def delete_task(self, task_id: int) -> bool:
        """Supprime une tâche"""
        session = self.db_service.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            session.delete(task)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la suppression de la tâche : {e}")
            return False
        finally:
            session.close()
    
    def mark_completed(self, task_id: int) -> bool:
        """Marque une tâche comme terminée"""
        return self.update_task(task_id, status='completed', is_completed=True)
    
    def mark_pending(self, task_id: int) -> bool:
        """Marque une tâche comme en attente"""
        return self.update_task(task_id, status='pending', is_completed=False)
    
    def search_tasks(self, query: str) -> List[Task]:
        """Recherche des tâches par titre ou description"""
        session = self.db_service.get_session()
        try:
            return session.query(Task).filter(
                Task.title.contains(query) | Task.description.contains(query)
            ).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la recherche : {e}")
            return []
        finally:
            session.close()
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des tâches"""
        session = self.db_service.get_session()
        try:
            total = session.query(Task).count()
            completed = session.query(Task).filter(Task.status == 'completed').count()
            pending = session.query(Task).filter(Task.status == 'pending').count()
            in_progress = session.query(Task).filter(Task.status == 'in_progress').count()
            
            return {
                'total': total,
                'completed': completed,
                'pending': pending,
                'in_progress': in_progress,
                'completion_rate': (completed / total * 100) if total > 0 else 0
            }
        except SQLAlchemyError as e:
            print(f"Erreur lors du calcul des statistiques : {e}")
            return {}
        finally:
            session.close()
