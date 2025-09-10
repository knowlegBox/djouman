"""
Test de la fenêtre minimale
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_minimal_window():
    """Test de la fenêtre minimale"""
    try:
        print("🔍 Test de la fenêtre minimale...")
        
        # Test 1: Import de base
        print("1. Import de base...")
        from PySide6.QtWidgets import QApplication
        print("   ✅ PySide6 OK")
        
        # Test 2: Création de l'application Qt
        print("2. Création de l'application Qt...")
        app = QApplication(sys.argv)
        print("   ✅ Application Qt créée")
        
        # Test 3: Test de création de la fenêtre minimale
        print("3. Test de création de la fenêtre minimale...")
        from ui.minimal_window import MinimalWindow
        window = MinimalWindow()
        print("   ✅ Fenêtre minimale créée")
        
        # Test 4: Affichage de la fenêtre
        print("4. Test d'affichage...")
        window.show()
        print("   ✅ Fenêtre affichée")
        
        app.quit()
        print("🎉 Test de la fenêtre minimale réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_window()
    sys.exit(0 if success else 1)
