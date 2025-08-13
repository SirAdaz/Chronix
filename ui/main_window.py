import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QProgressBar,
                             QComboBox, QSpinBox, QMessageBox, QFrame,
                             QGridLayout, QScrollArea, QGroupBox, QSplitter,
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tracker.db_manager as db_manager
from tracker.time_tracker import time_tracker
from tracker.icon_manager import icon_manager

class DarkTechTheme:
    """Thème Mode Sombre Tech avec couleurs néon"""
    
    # Couleurs principales
    BACKGROUND_DARK = "#0a0a0a"
    BACKGROUND_MEDIUM = "#1a1a1a"
    BACKGROUND_LIGHT = "#2a2a2a"
    
    # Couleurs néon
    NEON_BLUE = "#00d4ff"
    NEON_PURPLE = "#8a2be2"
    NEON_GREEN = "#00ff41"
    NEON_ORANGE = "#ff6b35"
    NEON_PINK = "#ff0080"
    
    # Couleurs de texte
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#808080"
    
    # Couleurs d'état
    SUCCESS = NEON_GREEN
    WARNING = NEON_ORANGE
    ERROR = "#ff4444"
    INFO = NEON_BLUE

class StatsWorker(QThread):
    """Thread pour mettre à jour les statistiques en arrière-plan"""
    stats_updated = pyqtSignal()
    
    def run(self):
        while True:
            self.stats_updated.emit()
            self.msleep(5000)  # Mise à jour toutes les 5 secondes

class ChronixMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chronix - Tracker de Temps")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialiser la base de données
        db_manager.init_db()
        
        # Appliquer le thème sombre
        self.apply_dark_theme()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer le tracking
        time_tracker.start_tracking()
        
        # Timer pour mettre à jour l'interface
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_current_session)
        self.update_timer.start(1000)  # Mise à jour toutes les secondes
        
        # Thread pour les statistiques
        self.stats_worker = StatsWorker()
        self.stats_worker.stats_updated.connect(self.update_stats)
        self.stats_worker.start()
        
        # Variable pour le démarrage automatique
        self.startup_enabled = self.check_startup_status()
        
        # Créer l'icône système tray
        self.setup_system_tray()

    def apply_dark_theme(self):
        """Applique le thème sombre tech"""
        palette = QPalette()
        
        # Couleurs de base
        palette.setColor(QPalette.ColorRole.Window, QColor(DarkTechTheme.BACKGROUND_DARK))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(DarkTechTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, QColor(DarkTechTheme.BACKGROUND_MEDIUM))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DarkTechTheme.BACKGROUND_LIGHT))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(DarkTechTheme.BACKGROUND_MEDIUM))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(DarkTechTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Text, QColor(DarkTechTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Button, QColor(DarkTechTheme.BACKGROUND_LIGHT))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(DarkTechTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Link, QColor(DarkTechTheme.NEON_BLUE))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(DarkTechTheme.NEON_PURPLE))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(DarkTechTheme.TEXT_PRIMARY))
        
        self.setPalette(palette)
        
        # Style CSS pour les widgets
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #2a2a2a;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #b0b0b0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #00d4ff;
                color: #000000;
            }
            QTabBar::tab:hover {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00d4ff;
                color: #000000;
                border: 1px solid #00d4ff;
            }
            QPushButton:pressed {
                background-color: #0088cc;
            }
            QTableWidget {
                background-color: #1a1a1a;
                alternate-background-color: #2a2a2a;
                color: #ffffff;
                gridline-color: #404040;
                border: 1px solid #404040;
            }
            QTableWidget::item:selected {
                background-color: #00d4ff;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #404040;
            }
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                color: #ffffff;
                padding: 6px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QSpinBox {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                color: #ffffff;
                padding: 6px;
                border-radius: 4px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                color: #00d4ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def setup_ui(self):
        """Configure l'interface utilisateur principale"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # En-tête avec titre et statut
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Onglets principaux
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_dashboard_tab(), "📊 Tableau de Bord")
        self.tab_widget.addTab(self.create_stats_tab(), "📈 Statistiques")
        self.tab_widget.addTab(self.create_quotas_tab(), "⏰ Quotas")
        self.tab_widget.addTab(self.create_settings_tab(), "⚙️ Paramètres")
        
        main_layout.addWidget(self.tab_widget)

    def create_header(self):
        """Crée l'en-tête avec le titre et les informations de session"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        
        # Titre
        title_label = QLabel("CHRONIX")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00d4ff;
            font-family: 'Consolas', monospace;
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Statut du tracking
        self.tracking_status = QLabel("🔵 Tracking actif")
        self.tracking_status.setStyleSheet("""
            font-size: 14px;
            color: #00ff41;
            font-weight: bold;
        """)
        layout.addWidget(self.tracking_status)
        
        # Session en cours
        self.current_session_label = QLabel("Aucune session active")
        self.current_session_label.setStyleSheet("""
            font-size: 14px;
            color: #b0b0b0;
        """)
        layout.addWidget(self.current_session_label)
        
        return header_frame

    def create_dashboard_tab(self):
        """Crée l'onglet tableau de bord"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Résumé d'aujourd'hui
        today_group = QGroupBox("📅 Aujourd'hui")
        today_layout = QGridLayout(today_group)
        
        self.today_total_label = QLabel("Temps total: 0h 0m")
        self.today_total_label.setStyleSheet("font-size: 18px; color: #00d4ff; font-weight: bold;")
        today_layout.addWidget(self.today_total_label, 0, 0)
        
        self.today_apps_label = QLabel("Applications: 0")
        self.today_apps_label.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        today_layout.addWidget(self.today_apps_label, 0, 1)
        
        layout.addWidget(today_group)
        
        # Top applications
        top_group = QGroupBox("🏆 Top Applications")
        top_layout = QVBoxLayout(top_group)
        
        self.top_apps_table = QTableWidget()
        self.top_apps_table.setColumnCount(3)
        self.top_apps_table.setHorizontalHeaderLabels(["Application", "Temps", "Pourcentage"])
        self.top_apps_table.horizontalHeader().setStretchLastSection(True)
        top_layout.addWidget(self.top_apps_table)
        
        layout.addWidget(top_group)
        
        # Graphique en temps réel
        chart_group = QGroupBox("📊 Activité en Temps Réel")
        chart_layout = QVBoxLayout(chart_group)
        
        self.figure = Figure(figsize=(10, 6), facecolor='#1a1a1a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')
        chart_layout.addWidget(self.canvas)
        
        layout.addWidget(chart_group)
        
        layout.addStretch()
        return widget

    def create_stats_tab(self):
        """Crée l'onglet statistiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Contrôles de période
        controls_layout = QHBoxLayout()
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Aujourd'hui", "Cette semaine", "Ce mois", "Semaine dernière", "Mois dernier"])
        self.period_combo.currentTextChanged.connect(self.update_stats)
        controls_layout.addWidget(QLabel("Période:"))
        controls_layout.addWidget(self.period_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Tableau des statistiques
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Application", "Temps", "Pourcentage", "Sessions"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.stats_table)
        
        return widget

    def create_quotas_tab(self):
        """Crée l'onglet gestion des quotas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Ajouter un quota
        add_group = QGroupBox("➕ Ajouter un Quota")
        add_layout = QGridLayout(add_group)
        
        self.app_combo = QComboBox()
        self.update_app_combo()
        add_layout.addWidget(QLabel("Application:"), 0, 0)
        add_layout.addWidget(self.app_combo, 0, 1)
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 1440)  # 1 minute à 24h
        self.limit_spin.setValue(120)  # 2h par défaut
        self.limit_spin.setSuffix(" minutes")
        add_layout.addWidget(QLabel("Limite quotidienne:"), 1, 0)
        add_layout.addWidget(self.limit_spin, 1, 1)
        
        add_btn = QPushButton("Ajouter Quota")
        add_btn.clicked.connect(self.add_quota)
        add_layout.addWidget(add_btn, 2, 0, 1, 2)
        
        layout.addWidget(add_group)
        
        # Quotas existants
        quotas_group = QGroupBox("📋 Quotas Configurés")
        quotas_layout = QVBoxLayout(quotas_group)
        
        self.quotas_table = QTableWidget()
        self.quotas_table.setColumnCount(4)
        self.quotas_table.setHorizontalHeaderLabels(["Application", "Limite", "Utilisé", "Progression"])
        self.quotas_table.horizontalHeader().setStretchLastSection(True)
        quotas_layout.addWidget(self.quotas_table)
        
        layout.addWidget(quotas_group)
        
        return widget

    def create_settings_tab(self):
        """Crée l'onglet paramètres"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Contrôles du tracking
        tracking_group = QGroupBox("🔍 Contrôles du Tracking")
        tracking_layout = QVBoxLayout(tracking_group)
        
        self.tracking_btn = QPushButton("Arrêter le Tracking")
        self.tracking_btn.clicked.connect(self.toggle_tracking)
        tracking_layout.addWidget(self.tracking_btn)
        
        layout.addWidget(tracking_group)
        
        # Base de données
        db_group = QGroupBox("🗄️ Base de Données")
        db_layout = QVBoxLayout(db_group)
        
        clear_btn = QPushButton("Vider l'historique")
        clear_btn.clicked.connect(self.clear_history)
        db_layout.addWidget(clear_btn)
        
        layout.addWidget(db_group)
        
        layout.addStretch()
        return widget

    def update_current_session(self):
        """Met à jour l'affichage de la session en cours"""
        session_info = time_tracker.get_current_session_info()
        
        if session_info:
            duration = time_tracker.format_duration(session_info["duration"])
            self.current_session_label.setText(f"Session: {session_info['app_name']} - {duration}")
        else:
            self.current_session_label.setText("Aucune session active")

    def update_stats(self):
        """Met à jour toutes les statistiques"""
        self.update_today_summary()
        self.update_top_apps()
        self.update_stats_table()
        self.update_quotas_table()
        self.update_chart()
        self.update_app_combo()

    def update_app_combo(self):
        """Met à jour le combo box des applications avec les icônes"""
        self.app_combo.clear()
        apps = db_manager.get_all_apps()
        
        for app_name, app_path in apps:
            # Récupérer l'icône de l'application
            icon = icon_manager.get_cached_icon(app_name, app_path)
            if not icon:
                icon = icon_manager.get_default_icon()
            
            self.app_combo.addItem(icon, app_name)

    def update_today_summary(self):
        """Met à jour le résumé d'aujourd'hui"""
        summary = time_tracker.get_today_summary()
        
        total_time = time_tracker.format_duration(summary["total_time"])
        self.today_total_label.setText(f"Temps total: {total_time}")
        self.today_apps_label.setText(f"Applications: {summary['apps_count']}")

    def update_top_apps(self):
        """Met à jour le tableau des top applications"""
        stats = db_manager.get_daily_stats()
        total_time = sum(seconds for _, seconds in stats)
        
        self.top_apps_table.setRowCount(len(stats[:10]))
        
        for i, (app_name, seconds) in enumerate(stats[:10]):
            duration = time_tracker.format_duration(seconds)
            percentage = (seconds / total_time * 100) if total_time > 0 else 0
            
            self.top_apps_table.setItem(i, 0, QTableWidgetItem(app_name))
            self.top_apps_table.setItem(i, 1, QTableWidgetItem(duration))
            self.top_apps_table.setItem(i, 2, QTableWidgetItem(f"{percentage:.1f}%"))

    def update_stats_table(self):
        """Met à jour le tableau des statistiques"""
        period = self.period_combo.currentText()
        
        if period == "Aujourd'hui":
            stats = db_manager.get_daily_stats()
        elif period == "Cette semaine":
            stats = db_manager.get_weekly_stats()
        elif period == "Ce mois":
            stats = db_manager.get_monthly_stats()
        elif period == "Semaine dernière":
            stats = db_manager.get_weekly_stats(1)
        elif period == "Mois dernier":
            stats = db_manager.get_monthly_stats(1)
        else:
            stats = []
        
        total_time = sum(seconds for _, seconds in stats)
        
        self.stats_table.setRowCount(len(stats))
        
        for i, (app_name, seconds) in enumerate(stats):
            duration = time_tracker.format_duration(seconds)
            percentage = (seconds / total_time * 100) if total_time > 0 else 0
            
            self.stats_table.setItem(i, 0, QTableWidgetItem(app_name))
            self.stats_table.setItem(i, 1, QTableWidgetItem(duration))
            self.stats_table.setItem(i, 2, QTableWidgetItem(f"{percentage:.1f}%"))
            self.stats_table.setItem(i, 3, QTableWidgetItem("N/A"))  # Sessions count

    def update_quotas_table(self):
        """Met à jour le tableau des quotas"""
        quotas = db_manager.get_quotas()
        
        self.quotas_table.setRowCount(len(quotas))
        
        for i, (app_name, limit_minutes) in enumerate(quotas):
            used_seconds, limit_seconds, percentage = db_manager.get_quota_usage(app_name)
            
            used_time = time_tracker.format_duration(used_seconds)
            limit_time = time_tracker.format_duration(limit_seconds)
            
            self.quotas_table.setItem(i, 0, QTableWidgetItem(app_name))
            self.quotas_table.setItem(i, 1, QTableWidgetItem(limit_time))
            self.quotas_table.setItem(i, 2, QTableWidgetItem(used_time))
            
            # Barre de progression
            progress = QProgressBar()
            progress.setValue(int(percentage))
            if percentage > 100:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
            elif percentage > 80:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #ff6b35; }")
            else:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #00d4ff; }")
            
            self.quotas_table.setCellWidget(i, 3, progress)

    def update_chart(self):
        """Met à jour le graphique d'activité"""
        self.ax.clear()
        
        # Données d'exemple pour le graphique
        stats = db_manager.get_daily_stats()
        if stats:
            apps = [app for app, _ in stats[:5]]
            times = [seconds/3600 for _, seconds in stats[:5]]  # Convertir en heures
            
            # Tronquer les noms d'applications pour éviter le débordement
            truncated_apps = []
            for app in apps:
                if len(app) > 12:
                    truncated_apps.append(app[:10] + "...")
                else:
                    truncated_apps.append(app)
            
            colors = [DarkTechTheme.NEON_BLUE, DarkTechTheme.NEON_PURPLE, 
                     DarkTechTheme.NEON_GREEN, DarkTechTheme.NEON_ORANGE, 
                     DarkTechTheme.NEON_PINK]
            
            bars = self.ax.bar(truncated_apps, times, color=colors[:len(truncated_apps)])
            self.ax.set_ylabel('Heures', color='white', fontsize=12)
            self.ax.set_title('Activité Aujourd\'hui', color='white', fontsize=16, fontweight='bold')
            
            # Personnaliser les axes
            self.ax.tick_params(colors='white', labelsize=10)
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['top'].set_color('white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['right'].set_color('white')
            
            # Rotation des labels et ajustement de la taille
            plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right', fontsize=9)
            
            # Ajouter les valeurs sur les barres
            for i, (bar, time_val) in enumerate(zip(bars, times)):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{time_val:.1f}h', ha='center', va='bottom', 
                           color='white', fontsize=9, fontweight='bold')
        
        self.canvas.draw()

    def add_quota(self):
        """Ajoute un nouveau quota"""
        app_name = self.app_combo.currentText()
        limit_minutes = self.limit_spin.value()
        
        if app_name:
            db_manager.add_quota(app_name, limit_minutes)
            self.update_quotas_table()
            QMessageBox.information(self, "Succès", f"Quota ajouté pour {app_name}")

    def toggle_tracking(self):
        """Active/désactive le tracking"""
        if time_tracker.is_tracking:
            time_tracker.stop_tracking()
            self.tracking_btn.setText("Démarrer le Tracking")
            self.tracking_status.setText("🔴 Tracking arrêté")
            self.tracking_status.setStyleSheet("color: #ff4444; font-weight: bold;")
        else:
            time_tracker.start_tracking()
            self.tracking_btn.setText("Arrêter le Tracking")
            self.tracking_status.setText("🔵 Tracking actif")
            self.tracking_status.setStyleSheet("color: #00ff41; font-weight: bold;")

    def clear_history(self):
        """Vide l'historique des sessions"""
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Êtes-vous sûr de vouloir vider tout l'historique ?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Ici on pourrait ajouter une fonction pour vider la base
            QMessageBox.information(self, "Info", "Fonctionnalité à implémenter")

    def setup_system_tray(self):
        """Configure l'icône système tray"""
        # Créer l'icône
        self.tray_icon = QSystemTrayIcon(self)
        
        # Créer une icône simple (cercle bleu avec "C")
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 212, 255))  # Couleur néon bleue
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Chronix - Tracker de Temps")
        
        # Créer le menu contextuel
        tray_menu = QMenu()
        
        # Action pour afficher/masquer la fenêtre
        show_action = QAction("Afficher Chronix", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        # Action pour démarrer/arrêter le tracking
        self.tracking_action = QAction("Arrêter le Tracking", self)
        self.tracking_action.triggered.connect(self.toggle_tracking_from_tray)
        tray_menu.addAction(self.tracking_action)
        
        tray_menu.addSeparator()
        
        # Action pour le démarrage automatique
        self.startup_action = QAction("Démarrage automatique", self)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.startup_enabled)
        self.startup_action.triggered.connect(self.toggle_startup)
        tray_menu.addAction(self.startup_action)
        
        tray_menu.addSeparator()
        
        # Action pour quitter
        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connecter le double-clic pour afficher la fenêtre
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Gestion du clic sur l'icône tray"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def toggle_tracking_from_tray(self):
        """Active/désactive le tracking depuis le tray"""
        if time_tracker.is_tracking:
            time_tracker.stop_tracking()
            self.tracking_action.setText("Démarrer le Tracking")
            self.tracking_btn.setText("Démarrer le Tracking")
            self.tracking_status.setText("🔴 Tracking arrêté")
            self.tracking_status.setStyleSheet("color: #ff4444; font-weight: bold;")
        else:
            time_tracker.start_tracking()
            self.tracking_action.setText("Arrêter le Tracking")
            self.tracking_btn.setText("Arrêter le Tracking")
            self.tracking_status.setText("🔵 Tracking actif")
            self.tracking_status.setStyleSheet("color: #00ff41; font-weight: bold;")

    def check_startup_status(self):
        """Vérifie si l'application est configurée pour le démarrage automatique"""
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "Chronix")
            winreg.CloseKey(key)
            return True
        except:
            return False

    def toggle_startup(self):
        """Active/désactive le démarrage automatique"""
        import winreg
        import sys
        import os
        
        if self.startup_action.isChecked():
            # Ajouter au démarrage automatique
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_WRITE)
                app_path = f'"{sys.executable}" "{os.path.abspath("main.py")}"'
                winreg.SetValueEx(key, "Chronix", 0, winreg.REG_SZ, app_path)
                winreg.CloseKey(key)
                self.startup_enabled = True
                self.tray_icon.showMessage("Chronix", "Démarrage automatique activé", 
                                         QSystemTrayIcon.MessageIcon.Information, 2000)
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible d'activer le démarrage automatique: {e}")
                self.startup_action.setChecked(False)
        else:
            # Supprimer du démarrage automatique
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_WRITE)
                winreg.DeleteValue(key, "Chronix")
                winreg.CloseKey(key)
                self.startup_enabled = False
                self.tray_icon.showMessage("Chronix", "Démarrage automatique désactivé", 
                                         QSystemTrayIcon.MessageIcon.Information, 2000)
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de désactiver le démarrage automatique: {e}")
                self.startup_action.setChecked(True)

    def quit_application(self):
        """Quitte complètement l'application"""
        time_tracker.stop_tracking()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        # Au lieu de fermer, masquer la fenêtre et garder l'app en arrière-plan
        self.hide()
        self.tray_icon.showMessage("Chronix", "Chronix continue de tracker en arrière-plan", 
                                 QSystemTrayIcon.MessageIcon.Information, 2000)
        event.ignore()
