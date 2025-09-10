"""
Service de gestion des catégories
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.category import Category
from .database import DatabaseService


class CategoryService:
    """Service de gestion des catégories"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    def create_category(self, name: str, description: str = None, 
                       color: str = "#3498db", icon: str = None) -> Optional[Category]:
        """Crée une nouvelle catégorie"""
        session = self.db_service.get_session()
        try:
            category = Category(
                name=name,
                description=description,
                color=color,
                icon=icon
            )
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la création de la catégorie : {e}")
            return None
        finally:
            session.close()
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Récupère une catégorie par son ID"""
        session = self.db_service.get_session()
        try:
            return session.query(Category).filter(Category.id == category_id).first()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération de la catégorie : {e}")
            return None
        finally:
            session.close()
    
    def get_all_categories(self) -> List[Category]:
        """Récupère toutes les catégories"""
        session = self.db_service.get_session()
        try:
            return session.query(Category).order_by(Category.name).all()
        except SQLAlchemyError as e:
            print(f"Erreur lors de la récupération des catégories : {e}")
            return []
        finally:
            session.close()
    
    def update_category(self, category_id: int, **kwargs) -> bool:
        """Met à jour une catégorie"""
        session = self.db_service.get_session()
        try:
            category = session.query(Category).filter(Category.id == category_id).first()
            if not category:
                return False
            
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la mise à jour de la catégorie : {e}")
            return False
        finally:
            session.close()
    
    def delete_category(self, category_id: int) -> bool:
        """Supprime une catégorie"""
        session = self.db_service.get_session()
        try:
            category = session.query(Category).filter(Category.id == category_id).first()
            if not category:
                return False
            
            session.delete(category)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur lors de la suppression de la catégorie : {e}")
            return False
        finally:
            session.close()
    
    def get_default_categories(self) -> List[Category]:
        """Crée les catégories par défaut"""
        default_categories = [
            {"name": "Travail", "color": "#e74c3c", "icon": "briefcase"},
            {"name": "Personnel", "color": "#3498db", "icon": "user"},
            {"name": "Maison", "color": "#2ecc71", "icon": "home"},
            {"name": "Santé", "color": "#f39c12", "icon": "heart"},
            {"name": "Loisirs", "color": "#9b59b6", "icon": "gamepad"}
        ]
        
        created_categories = []
        for cat_data in default_categories:
            category = self.create_category(**cat_data)
            if category:
                created_categories.append(category)
        
        return created_categories
