# window_tracker.py
import psutil
import win32gui
import win32process
import time
from datetime import datetime

current_app = None
start_time = None

def get_foreground_window_info():
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
    global current_app, start_time
    current_app = app_info
    start_time = datetime.now()
    print(f"[START] {current_app['name']} at {start_time}")

def stop_tracking_window():
    global current_app, start_time
    if current_app and start_time:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[STOP] {current_app['name']} - Duration: {duration} sec")
    current_app = None
    start_time = None

def track_foreground_window():
    global current_app
    while True:
        app_info = get_foreground_window_info()
        if not current_app or app_info["pid"] != current_app["pid"]:
            stop_tracking_window()
            start_tracking_window(app_info)
        time.sleep(5)
