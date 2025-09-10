"""
Application Todo List Manager
Point d'entrée principal de l'application
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from services import DatabaseService, CategoryService
from config.settings import DEFAULT_STYLES


def setup_application():
    """Configure l'application Qt"""
    app = QApplication([])
    app.setApplicationName("Todo List Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TodoListApp")
    
    # Configuration des styles
    app.setStyleSheet(DEFAULT_STYLES)
    
    return app


def initialize_database():
    """Initialise la base de données et crée les tables"""
    try:
        db_service = DatabaseService()
        db_service.create_tables()
        print("✅ Base de données initialisée avec succès")
        return db_service
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données : {e}")
        raise


def create_default_categories(category_service):
    """Crée les catégories par défaut si elles n'existent pas"""
    try:
        existing_categories = category_service.get_all_categories()
        if not existing_categories:
            print("📁 Création des catégories par défaut...")
            default_categories = category_service.get_default_categories()
            print(f"✅ {len(default_categories)} catégories créées")
        else:
            print(f"📁 {len(existing_categories)} catégories existantes trouvées")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des catégories : {e}")


def show_error_dialog(title, message):
    """Affiche une boîte de dialogue d'erreur"""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText("Erreur de démarrage")
    msg_box.setDetailedText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


def main():
    """Fonction principale de l'application"""
    print("🚀 Démarrage de Todo List Manager...")
    
    try:
        # Configuration de l'application Qt
        app = setup_application()
        print("✅ Application Qt configurée")
        
        # Initialisation de la base de données
        db_service = initialize_database()
        
        # Création des services
        category_service = CategoryService(db_service)
        print("✅ Services créés")
        
        # Création des catégories par défaut
        create_default_categories(category_service)
        
        # Création de la fenêtre principale
        print("🖥️ Création de l'interface utilisateur...")
        window = MainWindow()
        window.show()
        print("✅ Interface utilisateur créée et affichée")
        
        # Message de démarrage réussi
        print("🎉 Application démarrée avec succès !")
        print("📝 Vous pouvez maintenant créer et gérer vos tâches")
        
        # Lancement de la boucle d'événements
        return app.exec()
        
    except ImportError as e:
        error_msg = f"Module manquant : {e}\n\nVeuillez installer les dépendances avec :\npip install -r requirements.txt"
        print(f"❌ {error_msg}")
        show_error_dialog("Erreur d'import", error_msg)
        return 1
        
    except Exception as e:
        error_msg = f"Erreur inattendue : {str(e)}\n\nVérifiez que tous les fichiers sont présents et que les dépendances sont installées."
        print(f"❌ {error_msg}")
        show_error_dialog("Erreur de démarrage", error_msg)
        return 1


if __name__ == "__main__":
    # Point d'entrée principal
    exit_code = main()
    sys.exit(exit_code)
