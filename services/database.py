"""
Service de configuration de la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models import Base, Task, Project  # Import des modèles pour enregistrement
from config.settings import DATABASE_URL

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False  # Nécessaire pour SQLite avec plusieurs threads
    },
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Création de la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseService:
    """Service de gestion de la base de données"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Retourne une nouvelle session de base de données"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Crée toutes les tables dans la base de données"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Supprime toutes les tables de la base de données"""
        Base.metadata.drop_all(bind=self.engine)
    
    def close(self):
        """Ferme la connexion à la base de données"""
        self.engine.dispose()
