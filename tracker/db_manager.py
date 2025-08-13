import sqlite3
import os
from datetime import datetime, timedelta

def init_db():
    """Initialise la base de données avec les tables sessions et quotas"""
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT UNIQUE,
            daily_limit_minutes INTEGER,
            enabled BOOLEAN DEFAULT 1
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

def get_daily_stats(date=None):
    """Récupère les statistiques quotidiennes"""
    if date is None:
        date = datetime.now().date()
    
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT app_name, SUM(duration_sec) as total_seconds
        FROM sessions 
        WHERE DATE(start_time) = ?
        GROUP BY app_name
        ORDER BY total_seconds DESC
    ''', (date.isoformat(),))
    
    results = cursor.fetchall()
    conn.close()
    
    return [(app_name, seconds) for app_name, seconds in results]

def get_weekly_stats(weeks_back=0):
    """Récupère les statistiques hebdomadaires"""
    end_date = datetime.now().date() - timedelta(weeks=weeks_back)
    start_date = end_date - timedelta(days=6)
    
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT app_name, SUM(duration_sec) as total_seconds
        FROM sessions 
        WHERE DATE(start_time) BETWEEN ? AND ?
        GROUP BY app_name
        ORDER BY total_seconds DESC
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    results = cursor.fetchall()
    conn.close()
    
    return [(app_name, seconds) for app_name, seconds in results]

def get_monthly_stats(months_back=0):
    """Récupère les statistiques mensuelles"""
    end_date = datetime.now().date()
    start_date = end_date.replace(day=1) - timedelta(days=months_back * 30)
    
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT app_name, SUM(duration_sec) as total_seconds
        FROM sessions 
        WHERE DATE(start_time) >= ?
        GROUP BY app_name
        ORDER BY total_seconds DESC
    ''', (start_date.isoformat(),))
    
    results = cursor.fetchall()
    conn.close()
    
    return [(app_name, seconds) for app_name, seconds in results]

def get_all_apps():
    """Récupère la liste de toutes les applications utilisées"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT app_name, app_path
        FROM sessions 
        ORDER BY app_name
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [(app_name, app_path) for app_name, app_path in results]

def get_app_path(app_name):
    """Récupère le chemin d'une application"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT app_path 
        FROM sessions 
        WHERE app_name = ?
        LIMIT 1
    ''', (app_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def add_quota(app_name, daily_limit_minutes):
    """Ajoute ou met à jour un quota pour une application"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO quotas (app_name, daily_limit_minutes, enabled)
        VALUES (?, ?, 1)
    ''', (app_name, daily_limit_minutes))
    
    conn.commit()
    conn.close()

def remove_quota(app_name):
    """Supprime un quota pour une application"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM quotas WHERE app_name = ?', (app_name,))
    
    conn.commit()
    conn.close()

def get_quotas():
    """Récupère tous les quotas configurés"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT app_name, daily_limit_minutes FROM quotas WHERE enabled = 1')
    
    results = cursor.fetchall()
    conn.close()
    
    return [(app_name, minutes) for app_name, minutes in results]

def check_quota_exceeded(app_name):
    """Vérifie si le quota quotidien d'une application est dépassé"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    # Récupérer le quota
    cursor.execute('SELECT daily_limit_minutes FROM quotas WHERE app_name = ? AND enabled = 1', (app_name,))
    quota_result = cursor.fetchone()
    
    if not quota_result:
        conn.close()
        return False
    
    daily_limit_seconds = quota_result[0] * 60
    
    # Récupérer l'utilisation d'aujourd'hui
    today = datetime.now().date()
    cursor.execute('''
        SELECT SUM(duration_sec) 
        FROM sessions 
        WHERE app_name = ? AND DATE(start_time) = ?
    ''', (app_name, today.isoformat()))
    
    usage_result = cursor.fetchone()
    today_usage = usage_result[0] if usage_result[0] else 0
    
    conn.close()
    
    return today_usage >= daily_limit_seconds

def get_quota_usage(app_name):
    """Récupère l'utilisation actuelle d'une application par rapport à son quota"""
    conn = sqlite3.connect("chronix.db")
    cursor = conn.cursor()
    
    # Récupérer le quota
    cursor.execute('SELECT daily_limit_minutes FROM quotas WHERE app_name = ? AND enabled = 1', (app_name,))
    quota_result = cursor.fetchone()
    
    if not quota_result:
        conn.close()
        return 0, 0, 0
    
    daily_limit_seconds = quota_result[0] * 60
    
    # Récupérer l'utilisation d'aujourd'hui
    today = datetime.now().date()
    cursor.execute('''
        SELECT SUM(duration_sec) 
        FROM sessions 
        WHERE app_name = ? AND DATE(start_time) = ?
    ''', (app_name, today.isoformat()))
    
    usage_result = cursor.fetchone()
    today_usage = usage_result[0] if usage_result[0] else 0
    
    conn.close()
    
    percentage = (today_usage / daily_limit_seconds) * 100 if daily_limit_seconds > 0 else 0
    return today_usage, daily_limit_seconds, percentage 