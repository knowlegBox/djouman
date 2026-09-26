from sqlalchemy.orm import Session
from datetime import datetime
from models import WorkSession, Task, Project
from sqlalchemy import func

class WorkSessionService:
    """Service pour gérer les sessions de travail (suivi du temps)"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        
    def start_session(self, task_id: int, notes: str = None) -> WorkSession:
        """Démarre une nouvelle session de travail pour une tâche donnée.
        Arrête automatiquement toute autre session en cours."""
        session = self.db_service.get_session()
        try:
            # 1. Arrêter les sessions en cours
            active_sessions = session.query(WorkSession).filter(WorkSession.end_time.is_(None)).all()
            for s in active_sessions:
                s.end_time = datetime.utcnow()
                delta = s.end_time - s.start_time
                s.duration = int(delta.total_seconds())
                
            # 2. Créer une nouvelle session
            new_session = WorkSession(task_id=task_id, start_time=datetime.utcnow(), notes=notes)
            session.add(new_session)
            session.commit()
            
            # Recharger avec relations
            from sqlalchemy.orm import joinedload
            return session.query(WorkSession).options(joinedload(WorkSession.task).joinedload(Task.project)).filter(WorkSession.id == new_session.id).first()
        except Exception as e:
            session.rollback()
            print(f"Erreur lors du démarrage de la session: {e}")
            return None
            
    def stop_active_session(self) -> WorkSession:
        """Arrête la session de travail en cours, s'il y en a une"""
        session = self.db_service.get_session()
        try:
            active = session.query(WorkSession).filter(WorkSession.end_time.is_(None)).first()
            if active:
                active.end_time = datetime.utcnow()
                delta = active.end_time - active.start_time
                active.duration = int(delta.total_seconds())
                session.commit()
                return active
            return None
        except Exception as e:
            session.rollback()
            print(f"Erreur lors de l'arrêt de la session: {e}")
            return None
            
    def get_active_session(self) -> WorkSession:
        """Récupère la session de travail active"""
        session = self.db_service.get_session()
        from sqlalchemy.orm import joinedload
        return session.query(WorkSession).options(joinedload(WorkSession.task).joinedload(Task.project)).filter(WorkSession.end_time.is_(None)).first()
        
    def get_task_sessions(self, task_id: int):
        """Récupère l'historique des sessions pour une tâche"""
        session = self.db_service.get_session()
        return session.query(WorkSession).filter(WorkSession.task_id == task_id).order_by(WorkSession.start_time.desc()).all()
        
    def get_task_total_time(self, task_id: int) -> int:
        """Retourne le temps total passé sur une tâche (en secondes)"""
        session = self.db_service.get_session()
        total = session.query(func.sum(WorkSession.duration)).filter(WorkSession.task_id == task_id).scalar()
        
        # Ajouter le temps de la session en cours
        active = session.query(WorkSession).filter(WorkSession.task_id == task_id, WorkSession.end_time.is_(None)).first()
        if active:
            delta = datetime.utcnow() - active.start_time
            total = (total or 0) + int(delta.total_seconds())
            
        return total or 0
        
    def get_project_total_time(self, project_id: int) -> int:
        """Retourne le temps total passé sur un projet (en secondes)"""
        session = self.db_service.get_session()
        # Jointure entre WorkSession et Task
        total = session.query(func.sum(WorkSession.duration)).join(Task).filter(Task.project_id == project_id).scalar()
        
        # Ajouter le temps de la session en cours si elle appartient à ce projet
        active = session.query(WorkSession).join(Task).filter(Task.project_id == project_id, WorkSession.end_time.is_(None)).first()
        if active:
            delta = datetime.utcnow() - active.start_time
            total = (total or 0) + int(delta.total_seconds())
            
        return total or 0
