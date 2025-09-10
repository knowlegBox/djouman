# Todo List Manager

Une application de gestion de tâches moderne développée avec Python, PySide6 et SQLAlchemy.

## Structure du projet

```
djouman/
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation
├── config/
│   └── settings.py        # Configuration de l'application
├── models/
│   ├── __init__.py
│   ├── task.py           # Modèle de tâche
│   └── category.py       # Modèle de catégorie
├── services/
│   ├── __init__.py
│   ├── database.py       # Configuration de la base de données
│   ├── task_service.py   # Service de gestion des tâches
│   └── category_service.py # Service de gestion des catégories
├── ui/
│   ├── __init__.py
│   ├── main_window.py    # Fenêtre principale
│   ├── task_dialog.py    # Dialogue de création/édition de tâche
│   ├── category_dialog.py # Dialogue de gestion des catégories
│   └── widgets/
│       ├── __init__.py
│       ├── task_list.py  # Widget de liste des tâches
│       ├── task_item.py  # Widget d'élément de tâche
│       └── category_selector.py # Sélecteur de catégorie
├── utils/
│   ├── __init__.py
│   └── helpers.py        # Fonctions utilitaires
└── assets/
    ├── styles.css        # Styles CSS
    └── icons/           # Icônes de l'application
```

## Fonctionnalités

- ✅ Création, modification et suppression de tâches
- ✅ Gestion des catégories de tâches
- ✅ Priorités et durées des tâches
- ✅ Interface moderne avec PySide6
- ✅ Base de données SQLite avec SQLAlchemy
- ✅ Recherche et filtrage des tâches
- ✅ Sauvegarde automatique

## Installation

1. Cloner le projet
2. Installer les dépendances : `pip install -r requirements.txt`
3. Lancer l'application : `python main.py`

## Utilisation

L'application permet de :
- Ajouter de nouvelles tâches avec description, durée, priorité et catégorie
- Modifier ou supprimer des tâches existantes
- Organiser les tâches par catégories
- Filtrer les tâches par statut, priorité ou catégorie
- Visualiser les tâches dans une interface claire et intuitive
