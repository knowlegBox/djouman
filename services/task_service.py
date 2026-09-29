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
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions)).filter(Task.id == task_id).first()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de la tâche : {e}")
            return None
        finally:
            session.close()
    
    def get_all_tasks(self) -> List[Task]:
        """Récupère toutes les tâches (après synchronisation des JSON locaux)"""
        self.sync_all_projects()
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions)).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []
        finally:
            session.close()
            
    def sync_all_projects(self):
        """Synchronise les fichiers .djouman.json vers SQLite pour tous les projets"""
        session = self.db_service.get_session()
        try:
            from models.project import Project
            projects = session.query(Project).filter(Project.local_path != None, Project.local_path != "").all()
            for project in projects:
                self._sync_project_tasks_internal(project, session)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erreur globale de synchronisation JSON : {e}")
        finally:
            session.close()
            
    def _sync_project_tasks_internal(self, project, session):
        """Logique interne pour synchroniser un projet spécifique"""
        import os
        if not os.path.exists(project.local_path):
            return
            
        from .json_storage import JsonStorageService
        json_service = JsonStorageService(project.local_path)
        
        # S'assurer que les fichiers IA (instructions et raccourci /djouman) existent toujours
        json_service.setup_ai_integration()
        
        json_tasks = json_service.get_tasks()
        
        # Récupérer les tâches existantes
        db_tasks = session.query(Task).filter(Task.project_id == project.id).all()
        db_tasks_by_title = {t.title: t for t in db_tasks}
        
        # Fonction pour aplatir les tâches (support des epics)
        def extract_tasks(node, epic_name=None):
            extracted = []
            if isinstance(node, dict):
                title = node.get("title") or node.get("name")
                if title:
                    task_copy = node.copy()
                    if epic_name:
                        task_copy["epic_name"] = epic_name
                    extracted.append(task_copy)
                
                if "tasks" in node and isinstance(node["tasks"], list):
                    current_epic = node.get("epic") or epic_name
                    for subnode in node["tasks"]:
                        extracted.extend(extract_tasks(subnode, current_epic))
            elif isinstance(node, list):
                for item in node:
                    extracted.extend(extract_tasks(item, epic_name))
            return extracted
            
        flattened_tasks = extract_tasks(json_tasks)
        
        for j_task in flattened_tasks:
            title = j_task.get("title") or j_task.get("name")
            if not title:
                continue
                
            desc = j_task.get("description", "")
            epic_name = j_task.get("epic_name")
            if epic_name:
                desc = f"[Épopée: {epic_name}]\n{desc}"
                
            if "command" in j_task:
                desc = f"Commande: {j_task.get('command')}\n\n{desc}"
                
            # Extraire les sous-tâches (subtasks) du JSON en texte
            if "subtasks" in j_task and isinstance(j_task["subtasks"], list):
                subtasks_str = "\n".join([f"- {st}" for st in j_task["subtasks"] if isinstance(st, str)])
                if subtasks_str:
                    desc = f"{desc}\n\nSous-tâches:\n{subtasks_str}"
                
            raw_status = j_task.get("status", "pending").lower()
            if raw_status == "todo":
                status = "pending"
            elif raw_status == "done":
                status = "completed"
            elif raw_status == "in progress":
                status = "in_progress"
            else:
                status = raw_status
            
            # Map des priorités
            priority_str = str(j_task.get("priority", "moyen")).lower()
            priority_map = {"faible": 1, "moyen": 2, "élevé": 3}
            priority = priority_map.get(priority_str, 2)
            
            task_type = j_task.get("type", "feature")
            
            if title in db_tasks_by_title:
                db_task = db_tasks_by_title[title]
                # Mettre à jour si nécessaire
                if db_task.status != status or db_task.description != desc:
                    db_task.description = desc
                    db_task.status = status
                    db_task.priority = priority
                    db_task.task_type = task_type
            else:
                # Créer la nouvelle tâche
                new_task = Task(
                    title=title,
                    description=desc.strip(),
                    status=status,
                    priority=priority,
                    task_type=task_type,
                    project_id=project.id
                )
                session.add(new_task)
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Récupère les tâches par statut"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions)).filter(Task.status == status).order_by(Task.created_at.desc()).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []
        finally:
            session.close()
    
    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Récupère les tâches par projet"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions)).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()
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
            
            # Synchronisation retour vers le fichier .djouman.json
            if getattr(task, 'project', None) and task.project.local_path:
                import os
                if os.path.exists(task.project.local_path):
                    from .json_storage import JsonStorageService
                    json_service = JsonStorageService(task.project.local_path)
                    
                    json_data = json_service.read_data()
                    json_tasks = json_data.get("tasks", [])
                    
                    def update_json_task(nodes, target_title, new_status, new_start, new_end):
                        if isinstance(nodes, list):
                            for node in nodes:
                                if update_json_task(node, target_title, new_status, new_start, new_end):
                                    return True
                        elif isinstance(nodes, dict):
                            title = nodes.get("title") or nodes.get("name")
                            if title == target_title:
                                nodes["status"] = new_status
                                if new_start: nodes["start_date"] = new_start
                                if new_end: nodes["end_date"] = new_end
                                return True
                            
                            if "tasks" in nodes:
                                return update_json_task(nodes["tasks"], target_title, new_status, new_start, new_end)
                        return False
                        
                    update_json_task(
                        json_tasks, 
                        task.title, 
                        task.status, 
                        task.start_date.isoformat() if task.start_date else None, 
                        task.end_date.isoformat() if task.end_date else None
                    )
                            
                    json_data["tasks"] = json_tasks
                    json_service.write_data(json_data)
                    
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
