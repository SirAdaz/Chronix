import sqlite3
import os
from datetime import datetime

def init_db():
    """Initialise la base de données avec la table sessions"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT,
            app_path TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_sec INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_session(app_name, app_path, start_time, end_time, duration_sec):
    """Insère une nouvelle session dans la base de données"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (app_name, app_path, start_time, end_time, duration_sec)
        VALUES (?, ?, ?, ?, ?)
    ''', (app_name, app_path, start_time, end_time, duration_sec))
    
    conn.commit()
    conn.close()
    