import os
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import Qt

class IconManager:
    """Gestionnaire d'icônes pour les applications"""
    
    def __init__(self):
        self.icon_cache = {}
        self.app_colors = {
            "Chrome": "#4285f4",
            "Firefox": "#ff7139", 
            "Edge": "#0078d4",
            "Brave": "#ff2000",
            "Cursor": "#00d4ff",
            "VS Code": "#007acc",
            "Python": "#3776ab",
            "Discord": "#5865f2",
            "Steam": "#171a21",
            "Explorateur Windows": "#0078d4"
        }
    
    def get_app_icon(self, exe_path):
        """Crée une icône simple basée sur le nom de l'application"""
        # Extraire le nom de l'app depuis le chemin
        app_name = os.path.basename(exe_path).replace('.exe', '').title()
        
        # Créer une icône colorée avec la première lettre
        return self.create_text_icon(app_name[0] if app_name else "?", app_name)
    
    def create_text_icon(self, text, app_name):
        """Crée une icône avec du texte"""
        # Créer un pixmap
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
        
        # Choisir une couleur pour l'app
        color = self.app_colors.get(app_name, "#00d4ff")
        
        # Dessiner un cercle coloré
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Cercle de fond
        painter.setBrush(QColor(color))
        painter.setPen(QColor(color))
        painter.drawEllipse(2, 2, 28, 28)
        
        # Texte blanc
        painter.setPen(QColor("white"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        
        # Centrer le texte
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        
        return QIcon(pixmap)
    
    def get_cached_icon(self, app_name, exe_path):
        """Récupère une icône depuis le cache ou l'extrait"""
        if app_name in self.icon_cache:
            return self.icon_cache[app_name]
        
        icon = self.get_app_icon(exe_path)
        if icon:
            self.icon_cache[app_name] = icon
            
        return icon
    
    def get_default_icon(self):
        """Retourne une icône par défaut"""
        # Créer une icône simple (cercle bleu)
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 212, 255))  # Couleur néon bleue
        return QIcon(pixmap)

# Instance globale
icon_manager = IconManager()
