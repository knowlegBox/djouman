# 🌙 Djuma - Focus & Task Management

**Djuma** est une application de productivité moderne conçue pour vous aider à rester concentré et à accomplir vos tâches sans distraction. Développée en Python avec **PySide6** et **SQLAlchemy**, elle combine une gestion de tâches classique avec une fonctionnalité de "Screen Blocker" innovante.

---

## ✨ Fonctionnalités Principales

### 🎯 Gestion des Tâches Intelligente
- Création, édition et suppression de tâches en quelques clics.
- Gestion multi-sélection (modification de statuts ou suppression en lot).
- Planification précise : définissez une date/heure de début et de fin.
- Organisation avancée par **Catégories** (Travail, Personnel, Santé...) et par **Priorités** (Basse, Moyenne, Haute, Critique).

### 🌑 Mode Focus Absolu (Screen Blocker)
La fonctionnalité phare de Djuma :
- Lorsqu'une tâche arrive à son heure de début, un **écran noir minimaliste** s'affiche en plein écran, masquant toutes vos autres fenêtres.
- Cet écran affiche uniquement les détails de la tâche à accomplir, vous forçant à vous concentrer sur l'essentiel.
- Vous pouvez marquer la tâche comme terminée directement depuis cet écran, ou utiliser le mode *Snooze* pour la repousser.

### ⚙️ Panneau de Paramètres Personnalisable
- Un onglet dédié pour configurer le comportement de l'application.
- Ajustez le délai de *Snooze* (5, 10, 15 ou 30 minutes).
- Définissez la durée par défaut d'une nouvelle tâche.
- Désactivez le Screen Blocker si nécessaire, ou masquez automatiquement les tâches terminées pour garder un espace de travail épuré.

### 📊 Statistiques Visuelles
- Un graphique interactif s'affiche en temps réel pour suivre l'état d'avancement de vos tâches (En attente, En cours, Terminée).

---

## 🛠️ Stack Technique

- **Interface Graphique :** PySide6 (Qt pour Python)
- **Base de Données :** SQLite via l'ORM SQLAlchemy
- **Graphes :** QtCharts intégrés à PySide6
- **Compilation :** PyInstaller (script automatisé fourni)

---

## 🚀 Installation & Utilisation

### Prérequis
Assurez-vous d'avoir Python 3.14+ installé sur votre machine.

### Installation
1. Cloner le projet :
   ```bash
   git clone https://github.com/knowlegBox/djouman.git
   cd djouman
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l'application :
   ```bash
   python main.py
   ```

---

## 📦 Créer un exécutable (Windows)

Si vous souhaitez distribuer l'application ou l'utiliser sans lancer de terminal, vous pouvez créer un exécutable autonome `.exe` :

1. Placez une icône nommée `icon.ico` à la racine du projet.
2. Double-cliquez sur le fichier **`build.bat`**.
3. L'exécutable final se trouvera dans le dossier `dist/Djuma/Djuma.exe`.

---

*Prenez le contrôle de votre temps avec Djuma.*
