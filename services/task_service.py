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
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions), joinedload(Task.subtasks)).filter(Task.id == task_id).first()
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
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions), joinedload(Task.subtasks)).order_by(Task.created_at.desc()).all()
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
        
        json_data = json_service.read_data()
        json_tasks = json_data.get("tasks", [])
        if not json_tasks and "epics" in json_data:
            json_tasks = json_data.get("epics", [])
        
        # Récupérer les tâches existantes
        db_tasks = session.query(Task).filter(Task.project_id == project.id).all()
        db_tasks_by_title = {t.title: t for t in db_tasks}
        
        # Fonction pour aplatir les tâches (support des epics)
        def extract_tasks(node, epic_name=None):
            extracted = []
            if isinstance(node, dict):
                title = node.get("title") or node.get("name")
                has_tasks = "tasks" in node and isinstance(node["tasks"], list)
                
                if title and not has_tasks:
                    task_copy = node.copy()
                    if epic_name:
                        task_copy["epic_name"] = epic_name
                    extracted.append(task_copy)
                
                if has_tasks:
                    current_epic = node.get("epic") or title or epic_name
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
                current_task = db_task
            else:
                # Créer la nouvelle tâche
                current_task = Task(
                    title=title,
                    description=desc.strip(),
                    status=status,
                    priority=priority,
                    task_type=task_type,
                    project_id=project.id
                )
                session.add(current_task)
                session.flush() # Pour avoir l'ID
                
            if "duration" in j_task:
                current_task.duration = j_task.get("duration")
                
            # Gérer les vraies sous-tâches (modèle SubTask)
            if "subtasks" in j_task and isinstance(j_task["subtasks"], list):
                from models.subtask import SubTask
                existing_subtasks = session.query(SubTask).filter(SubTask.task_id == current_task.id).all()
                existing_titles = {st.title: st for st in existing_subtasks}
                
                for st in j_task["subtasks"]:
                    st_title = st if isinstance(st, str) else (st.get("title") or st.get("name"))
                    if st_title and st_title not in existing_titles:
                        new_st = SubTask(title=st_title, task_id=current_task.id)
                        if isinstance(st, dict):
                            if st.get("status", "").lower() in ["done", "completed"]:
                                new_st.is_completed = True
                            if "duration" in st:
                                new_st.duration = st.get("duration")
                        session.add(new_st)
                        existing_titles[st_title] = new_st
                    elif st_title in existing_titles:
                        # Mise à jour si elle existe déjà
                        if isinstance(st, dict):
                            if "duration" in st:
                                existing_titles[st_title].duration = st.get("duration")
                            if st.get("status", "").lower() in ["done", "completed"]:
                                existing_titles[st_title].is_completed = True
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Récupère les tâches par statut"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions), joinedload(Task.subtasks)).filter(Task.status == status).order_by(Task.created_at.desc()).all()
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
            return session.query(Task).options(joinedload(Task.project), joinedload(Task.work_sessions), joinedload(Task.subtasks)).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()
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
                    
                    def update_json_task(nodes, target_title, new_status, new_start, new_end, new_duration):
                        if isinstance(nodes, list):
                            for node in nodes:
                                if update_json_task(node, target_title, new_status, new_start, new_end, new_duration):
                                    return True
                        elif isinstance(nodes, dict):
                            title = nodes.get("title") or nodes.get("name")
                            if title == target_title and "tasks" not in nodes:
                                nodes["status"] = new_status
                                if new_start: nodes["start_date"] = new_start
                                if new_end: nodes["end_date"] = new_end
                                if new_duration is not None: nodes["duration"] = new_duration
                                return True
                            
                            if "tasks" in nodes:
                                return update_json_task(nodes["tasks"], target_title, new_status, new_start, new_end, new_duration)
                        return False
                        
                    if "tasks" in json_data:
                        update_json_task(json_data["tasks"], task.title, task.status, 
                            task.start_date.isoformat() if task.start_date else None, 
                            task.end_date.isoformat() if task.end_date else None,
                            task.duration)
                    elif "epics" in json_data:
                        update_json_task(json_data["epics"], task.title, task.status, 
                            task.start_date.isoformat() if task.start_date else None, 
                            task.end_date.isoformat() if task.end_date else None,
                            task.duration)
                            
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
    
    def sync_subtasks_to_json(self, task_id: int):
        """Synchronise les sous-tâches d'une tâche vers le fichier .djouman/tasks.json"""
        session = self.db_service.get_session()
        try:
            from sqlalchemy.orm import joinedload
            task = session.query(Task).options(joinedload(Task.project), joinedload(Task.subtasks)).filter(Task.id == task_id).first()
            if not task or not task.project or not task.project.local_path:
                return
            
            import os
            if not os.path.exists(task.project.local_path):
                return
            
            from .json_storage import JsonStorageService
            json_service = JsonStorageService(task.project.local_path)
            json_data = json_service.read_data()
            
            from models.subtask import SubTask
            subtasks = session.query(SubTask).filter(SubTask.task_id == task_id).order_by(SubTask.id.asc()).all()
            
            # Construire la liste des sous-tâches au format dict pour l'IA
            subtasks_json = []
            for st in subtasks:
                st_dict = {"title": st.title}
                if st.is_completed:
                    st_dict["status"] = "done"
                else:
                    st_dict["status"] = "pending"
                if st.duration:
                    st_dict["duration"] = st.duration
                subtasks_json.append(st_dict)
            
            def update_subtasks_in_json(nodes, target_title, new_subtasks):
                if isinstance(nodes, list):
                    for node in nodes:
                        if update_subtasks_in_json(node, target_title, new_subtasks):
                            return True
                elif isinstance(nodes, dict):
                    title = nodes.get("title") or nodes.get("name")
                    if title == target_title and "tasks" not in nodes:
                        nodes["subtasks"] = new_subtasks
                        return True
                    if "tasks" in nodes:
                        return update_subtasks_in_json(nodes["tasks"], target_title, new_subtasks)
                return False
            
            if "tasks" in json_data:
                update_subtasks_in_json(json_data["tasks"], task.title, subtasks_json)
            elif "epics" in json_data:
                update_subtasks_in_json(json_data["epics"], task.title, subtasks_json)
            
            json_service.write_data(json_data)
        except Exception as e:
            print(f"Erreur lors de la sync des sous-tâches vers JSON : {e}")
        finally:
            session.close()

    def update_parent_task_dates(self, task_id: int):
        """Met à jour les dates de la tâche parente en fonction de ses sous-tâches"""
        session = self.db_service.get_session()
        try:
            from models.subtask import SubTask
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task: return
            
            subtasks = session.query(SubTask).filter(SubTask.task_id == task_id).all()
            if not subtasks: return
            
            starts = [st.start_date for st in subtasks if st.start_date]
            ends = [st.end_date for st in subtasks if st.end_date]
            
            if starts:
                task.start_date = min(starts)
            if ends:
                task.end_date = max(ends)
            
            if task.start_date and task.end_date:
                diff = task.end_date - task.start_date
                task.duration = int(diff.total_seconds() / 60)
                
            session.commit()
            
            # Update json sync if needed
            self.update_task(task.id)
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur update_parent_task_dates : {e}")
        finally:
            session.close()
