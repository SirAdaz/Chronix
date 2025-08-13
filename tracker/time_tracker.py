import time
import threading
from datetime import datetime, timedelta
from . import db_manager
import psutil
import win32gui
import win32process

class TimeTracker:
    def __init__(self):
        self.current_app = None
        self.start_time = None
        self.is_tracking = False
        self.tracking_thread = None
        self.quota_alerts = {}
        
    def get_foreground_window_info(self):
        """Retourne les infos de la fenêtre actuellement au premier plan."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            proc = psutil.Process(pid)
            exe_path = proc.exe()
            name = proc.name()
            
            # Convertir le nom de l'exe en nom convivial
            friendly_name = self.get_friendly_app_name(name, exe_path)
            
            return {
                "pid": pid,
                "name": friendly_name,
                "exe_name": name,  # Garder le nom original pour la compatibilité
                "path": exe_path,
                "title": window_title
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return None

    def get_friendly_app_name(self, exe_name, exe_path):
        """Convertit le nom de l'exe en nom convivial de l'application"""
        # Dictionnaire de mapping pour les applications courantes
        app_names = {
            # Navigateurs
            "chrome.exe": "Chrome",
            "firefox.exe": "Firefox",
            "msedge.exe": "Edge",
            "brave.exe": "Brave",
            "opera.exe": "Opera",
            
            # Éditeurs de code
            "code.exe": "VS Code",
            "cursor.exe": "Cursor",
            "notepad++.exe": "Notepad++",
            "sublime_text.exe": "Sublime Text",
            "atom.exe": "Atom",
            "webstorm64.exe": "WebStorm",
            "pycharm64.exe": "PyCharm",
            "intellij64.exe": "IntelliJ IDEA",
            
            # Applications Microsoft
            "explorer.exe": "Explorateur Windows",
            "notepad.exe": "Bloc-notes",
            "wordpad.exe": "WordPad",
            "calc.exe": "Calculatrice",
            "mspaint.exe": "Paint",
            "winword.exe": "Microsoft Word",
            "excel.exe": "Microsoft Excel",
            "powerpnt.exe": "Microsoft PowerPoint",
            "outlook.exe": "Microsoft Outlook",
            "teams.exe": "Microsoft Teams",
            "skype.exe": "Skype",
            
            # Applications de communication
            "discord.exe": "Discord",
            "slack.exe": "Slack",
            "telegram.exe": "Telegram",
            "whatsapp.exe": "WhatsApp",
            
            # Applications de développement
            "python.exe": "Python",
            "node.exe": "Node.js",
            "git.exe": "Git",
            "docker.exe": "Docker",
            "postman.exe": "Postman",
            
            # Applications de design
            "photoshop.exe": "Adobe Photoshop",
            "illustrator.exe": "Adobe Illustrator",
            "figma.exe": "Figma",
            "sketch.exe": "Sketch",
            
            # Applications de jeux
            "steam.exe": "Steam",
            "epicgameslauncher.exe": "Epic Games",
            "origin.exe": "Origin",
            "battle.net.exe": "Battle.net",
            
            # Applications système
            "svchost.exe": "Service Windows",
            "winlogon.exe": "Windows Logon",
            "csrss.exe": "Client Server Runtime",
            "wininit.exe": "Windows Initialization",
            "services.exe": "Services Windows",
            "lsass.exe": "Local Security Authority",
            "spoolsv.exe": "Spooler Service",
            "taskmgr.exe": "Gestionnaire des tâches",
            "control.exe": "Panneau de configuration",
            "regedit.exe": "Éditeur de registre",
            "cmd.exe": "Invite de commandes",
            "powershell.exe": "PowerShell",
            "conhost.exe": "Console Host",
        }
        
        # Vérifier d'abord dans le dictionnaire
        if exe_name.lower() in app_names:
            return app_names[exe_name.lower()]
        
        # Si pas trouvé, essayer d'extraire le nom depuis le chemin
        if exe_path:
            try:
                # Extraire le nom du dossier parent (souvent le nom de l'app)
                import os
                parent_dir = os.path.basename(os.path.dirname(exe_path))
                
                # Nettoyer le nom
                clean_name = parent_dir.replace(" (x86)", "").replace(" (x64)", "")
                
                # Si le nom parent semble être un nom d'application (pas un chemin système)
                if not any(system_path in exe_path.lower() for system_path in [
                    "windows", "program files", "system32", "syswow64", "appdata"
                ]):
                    return clean_name
                    
            except:
                pass
        
        # En dernier recours, retourner le nom sans l'extension
        return exe_name.replace('.exe', '').title()

    def start_tracking(self):
        """Démarre le tracking en arrière-plan"""
        if not self.is_tracking:
            self.is_tracking = True
            self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self.tracking_thread.start()
            print("🔵 Tracking démarré")

    def stop_tracking(self):
        """Arrête le tracking"""
        self.is_tracking = False
        if self.current_app:
            self._stop_current_session()
        print("🔴 Tracking arrêté")

    def _tracking_loop(self):
        """Boucle principale de tracking"""
        while self.is_tracking:
            app_info = self.get_foreground_window_info()
            
            if app_info and app_info.get("name"):
                if not self.current_app or app_info["pid"] != self.current_app["pid"]:
                    self._stop_current_session()
                    self._start_new_session(app_info)
            
            time.sleep(2)  # Vérification toutes les 2 secondes

    def _start_new_session(self, app_info):
        """Démarre une nouvelle session pour l'application"""
        self.current_app = app_info
        self.start_time = datetime.now()
        print(f"🟢 Session démarrée: {self.current_app['name']}")

    def _stop_current_session(self):
        """Termine la session en cours et l'enregistre"""
        if self.current_app and self.start_time:
            end_time = datetime.now()
            duration = int((end_time - self.start_time).total_seconds())

            if duration > 0:  # Ignorer les sessions trop courtes
                db_manager.insert_session(
                    self.current_app['name'],  # Utilise maintenant le nom convivial
                    self.current_app.get('path', ''),
                    self.start_time.isoformat(),
                    end_time.isoformat(),
                    duration
                )
                
                # Vérifier les quotas
                self._check_quota_alert(self.current_app['name'], duration)

            print(f"🔴 Session terminée: {self.current_app['name']} - {duration}s")

        self.current_app = None
        self.start_time = None

    def _check_quota_alert(self, app_name, duration):
        """Vérifie si un quota est dépassé et génère une alerte"""
        if db_manager.check_quota_exceeded(app_name):
            if app_name not in self.quota_alerts:
                self.quota_alerts[app_name] = True
                print(f"⚠️  ALERTE: Quota dépassé pour {app_name}!")
                # Ici on pourrait ajouter une notification système
        else:
            # Réinitialiser l'alerte si le quota n'est plus dépassé
            self.quota_alerts.pop(app_name, None)

    def get_current_session_info(self):
        """Retourne les informations sur la session en cours"""
        if self.current_app and self.start_time:
            duration = int((datetime.now() - self.start_time).total_seconds())
            return {
                "app_name": self.current_app["name"],
                "start_time": self.start_time,
                "duration": duration
            }
        return None

    def get_today_summary(self):
        """Retourne un résumé de l'utilisation d'aujourd'hui"""
        stats = db_manager.get_daily_stats()
        total_time = sum(seconds for _, seconds in stats)
        
        return {
            "total_time": total_time,
            "apps_count": len(stats),
            "top_apps": stats[:5] if stats else []
        }

    def format_duration(self, seconds):
        """Formate une durée en secondes en format lisible"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

# Instance globale du tracker
time_tracker = TimeTracker()
