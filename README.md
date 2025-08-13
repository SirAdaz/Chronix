# Chronix

**Chronix** — Application de suivi et de gestion du temps passé sur chaque application de votre ordinateur. Elle détecte automatiquement les programmes en cours, enregistre leur durée d'utilisation, génère des statistiques (jour/semaine/mois) et permet de fixer des limites de temps pour favoriser une meilleure gestion de votre productivité.

## 🚀 Fonctionnalités

### ✨ Fonctionnalités principales
- **Détection automatique** des applications en cours d'exécution
- **Suivi en temps réel** du temps passé sur chaque application
- **Statistiques détaillées** (quotidiennes, hebdomadaires, mensuelles)
- **Système de quotas** pour limiter le temps d'utilisation
- **Interface moderne** avec thème "Mode Sombre Tech"
- **Graphiques interactifs** pour visualiser l'activité
- **Alertes intelligentes** quand les quotas sont dépassés

### 🎨 Interface utilisateur
- **Thème sombre** avec accents néon (bleu, violet, vert, orange)
- **Design moderne** inspiré des dashboards de développeur
- **Mise à jour en temps réel** des statistiques
- **Navigation intuitive** par onglets
- **Responsive** et adaptatif

## 📋 Prérequis

- **Windows 10/11** (testé sur Windows 10)
- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)

## 🛠️ Installation

### 1. Cloner le repository
```bash
git clone https://github.com/votre-username/chronix.git
cd chronix
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python main.py
```

## 🎯 Utilisation

### Démarrage rapide
1. Lancez l'application avec `python main.py`
2. Le tracking démarre automatiquement
3. Consultez vos statistiques dans l'onglet "Tableau de Bord"

### Onglets disponibles

#### 📊 Tableau de Bord
- **Résumé quotidien** : temps total et nombre d'applications
- **Top applications** : classement des apps les plus utilisées
- **Graphique d'activité** : visualisation en temps réel

#### 📈 Statistiques
- **Filtres temporels** : aujourd'hui, cette semaine, ce mois, etc.
- **Tableau détaillé** : temps, pourcentage, nombre de sessions
- **Export possible** des données

#### ⏰ Quotas
- **Ajouter des limites** : définir des quotas quotidiens par application
- **Suivi en temps réel** : barres de progression colorées
- **Alertes automatiques** : notifications quand les limites sont dépassées

#### ⚙️ Paramètres
- **Contrôle du tracking** : démarrer/arrêter le suivi
- **Gestion de la base** : vider l'historique
- **Configuration** : paramètres avancés

### Configuration des quotas
1. Allez dans l'onglet "Quotas"
2. Sélectionnez une application dans la liste
3. Définissez une limite quotidienne (en minutes)
4. Cliquez sur "Ajouter Quota"
5. Surveillez la progression dans le tableau

## 🏗️ Architecture

```
Chronix/
├── main.py                 # Point d'entrée principal
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation
├── chronix.db             # Base de données SQLite
├── tracker/               # Module de tracking
│   ├── __init__.py
│   ├── db_manager.py      # Gestion de la base de données
│   ├── time_tracker.py    # Logique de suivi du temps
│   └── window_tracker.py  # Détection des fenêtres
└── ui/                    # Interface utilisateur
    ├── __init__.py
    └── main_window.py     # Fenêtre principale PyQt6
```

## 🔧 Technologies utilisées

- **Python 3.8+** : Langage principal
- **PyQt6** : Interface graphique moderne
- **SQLite** : Base de données légère
- **psutil** : Détection des processus
- **pywin32** : API Windows pour la détection des fenêtres
- **matplotlib** : Graphiques et visualisations
- **threading** : Traitement en arrière-plan

## 🎨 Thème "Mode Sombre Tech"

L'application utilise un thème sombre avec des accents néon :

- **Fond principal** : Noir profond (#0a0a0a)
- **Fond secondaire** : Gris foncé (#1a1a1a, #2a2a2a)
- **Accents néon** : 
  - Bleu électrique (#00d4ff)
  - Violet (#8a2be2)
  - Vert néon (#00ff41)
  - Orange (#ff6b35)
  - Rose (#ff0080)

## 📊 Fonctionnalités avancées

### Système de tracking
- **Détection automatique** des changements de fenêtre
- **Enregistrement précis** des sessions (début/fin/durée)
- **Filtrage intelligent** des applications système
- **Threading** pour ne pas bloquer l'interface

### Base de données
- **SQLite** pour la portabilité
- **Tables optimisées** pour les requêtes fréquentes
- **Index automatiques** pour les performances
- **Sauvegarde automatique** des données

### Statistiques
- **Calculs en temps réel** des pourcentages
- **Filtres temporels** flexibles
- **Graphiques interactifs** avec matplotlib
- **Export possible** des données

## 🚨 Gestion des quotas

### Fonctionnement
1. **Définition** : Limite quotidienne par application
2. **Surveillance** : Vérification en temps réel
3. **Alertes** : Notifications visuelles
4. **Barres de progression** : Indication du niveau d'utilisation

### Couleurs des alertes
- **🟢 Vert** : < 80% du quota
- **🟠 Orange** : 80-100% du quota
- **🔴 Rouge** : > 100% du quota

## 🔒 Confidentialité

- **Données locales** : Toutes les données restent sur votre ordinateur
- **Aucune transmission** : Aucune donnée n'est envoyée à l'extérieur
- **Contrôle total** : Vous pouvez supprimer l'historique à tout moment

## 🐛 Dépannage

### Problèmes courants

#### L'application ne démarre pas
```bash
# Vérifier Python
python --version

# Réinstaller les dépendances
pip uninstall PyQt6 psutil pywin32 matplotlib numpy
pip install -r requirements.txt
```

#### Le tracking ne fonctionne pas
- Vérifiez que vous avez les droits administrateur
- Assurez-vous que Windows Defender n'empêche pas l'accès
- Redémarrez l'application

#### Erreurs de base de données
```bash
# Supprimer la base corrompue
rm chronix.db
# Relancer l'application (nouvelle base créée automatiquement)
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **PyQt6** pour l'interface graphique moderne
- **psutil** pour la détection des processus
- **matplotlib** pour les visualisations
- **SQLite** pour la base de données

---

**Développé avec ❤️ pour une meilleure gestion du temps** 
