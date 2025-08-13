import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ajouter le répertoire ui au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

from ui.main_window import ChronixMainWindow

def main():
    """Point d'entrée principal de l'application"""
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Chronix")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Chronix")
    
    # Créer et afficher la fenêtre principale
    window = ChronixMainWindow()
    window.show()
    
    # Lancer l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
