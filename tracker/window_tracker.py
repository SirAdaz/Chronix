# tracker/window_tracker.py
import psutil
import win32gui
import win32process
import time
from datetime import datetime
from tracker import db_manager

# Variables pour suivre la session en cours
current_app = None
start_time = None

def get_foreground_window_info():
    """Retourne les infos de la fenêtre actuellement au premier plan."""
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    try:
        proc = psutil.Process(pid)
        exe_path = proc.exe()
        name = proc.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        exe_path = None
        name = None

    return {
        "pid": pid,
        "name": name,
        "path": exe_path,
        "title": window_title
    }

def start_tracking_window(app_info):
    """Démarre une nouvelle session pour l'application donnée."""
    global current_app, start_time
    current_app = app_info
    start_time = datetime.now()
    print(f"[START] {current_app['name']} à {start_time}")

def stop_tracking_window():
    """Termine la session en cours et l'enregistre en base."""
    global current_app, start_time
    if current_app and start_time:
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())

        db_manager.insert_session(
            current_app['name'],
            current_app['path'],
            start_time.isoformat(),
            end_time.isoformat(),
            duration
        )

        print(f"[STOP] {current_app['name']} - Durée : {duration} sec enregistrée")

    current_app = None
    start_time = None

def track_foreground_window():
    """Boucle principale qui détecte les changements de fenêtre."""
    global current_app
    
    # Initialiser la base de données
    db_manager.init_db()
    
    while True:
        app_info = get_foreground_window_info()
        if not current_app or app_info["pid"] != current_app["pid"]:
            stop_tracking_window()
            start_tracking_window(app_info)
        time.sleep(5)
