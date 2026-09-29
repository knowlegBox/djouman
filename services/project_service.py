"""
Service de gestion des projets
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.project import Project
from .database import DatabaseService
from .json_storage import JsonStorageService

class ProjectService:
    """Service de gestion des projets"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def create_project(self, name: str, description: str = None, repo_url: str = None,
                       local_path: str = None, default_branch: str = None, tracker_url: str = None,
                       color: str = "#3498db", status: str = "actif",
                       start_date=None, end_date=None) -> Optional[Project]:
        """Crée un nouveau projet"""
        session = self.db_service.get_session()
        try:
            project = Project(
                name=name,
                description=description,
                repo_url=repo_url,
                local_path=local_path,
                default_branch=default_branch,
                tracker_url=tracker_url,
                color=color,
                status=status,
                start_date=start_date,
                end_date=end_date
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            
            # Création automatique du fichier .djouman.json et des intégrations IA
            if project.local_path:
                json_service = JsonStorageService(project.local_path)
                json_service.ensure_file_exists(project.name)
                json_service.setup_ai_integration()
                
            return project
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la création du projet : {e}")
            return None
        finally:
            session.close()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Récupère un projet par son ID"""
        session = self.db_service.get_session()
        try:
            return session.query(Project).filter(Project.id == project_id).first()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération du projet : {e}")
            return None
        finally:
            session.close()
    
    def get_all_projects(self) -> List[Project]:
        """Récupère tous les projets"""
        session = self.db_service.get_session()
        try:
            return session.query(Project).order_by(Project.name).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des projets : {e}")
            return []
        finally:
            session.close()
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Met à jour un projet"""
        session = self.db_service.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la mise à jour du projet : {e}")
            return False
        finally:
            session.close()
    
    def delete_project(self, project_id: int) -> bool:
        """Supprime un projet"""
        session = self.db_service.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            session.delete(project)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la suppression du projet : {e}")
            return False
        finally:
            session.close()
