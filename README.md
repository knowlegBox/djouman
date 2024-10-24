# djouman
une application desktop pour la productivité

---

### **Cahier des charges pour l'application desktop "Gestion de Tâches avec Timer Pomodoro"**

#### 1. **Contexte et objectifs du projet**
L'objectif est de développer une application desktop Python qui s'exécute automatiquement au démarrage de l'ordinateur. Cette application permet d'afficher le programme de la journée, de gérer les tâches programmées, et intègre un **timer Pomodoro** pour améliorer la productivité en suivant un cycle de travail et de pause.

Lorsque chaque tâche est terminée, une fenêtre s'affiche avec la tâche suivante, accompagnée d'un compteur de temps. Pendant les pauses du timer Pomodoro, l'écran reste noirci pour éviter toute distraction, maximisant ainsi la concentration de l'utilisateur.

#### 2. **Fonctionnalités principales**

##### 2.1. **Lancement automatique au démarrage**
- L'application doit démarrer automatiquement lorsque l'ordinateur est allumé (intégration au démarrage du système via le registre Windows ou la configuration Linux/OSX).
- Une option dans les paramètres permettra de désactiver ce lancement automatique.

##### 2.2. **Affichage du programme de la journée**
- L'utilisateur peut visualiser l'ensemble des tâches planifiées pour la journée à travers une interface simple.
- Les tâches sont organisées par ordre chronologique avec des indications sur l'heure de début et la durée.
- Un fichier de configuration (par exemple, JSON, YAML ou une base de données locale) permettra d’enregistrer et de modifier les tâches.

##### 2.3. **Gestion des tâches**
- Lorsqu'une tâche est terminée, l'application affiche automatiquement une fenêtre avec la tâche suivante.
- Chaque tâche inclut les informations suivantes :
  - Titre de la tâche
  - Description optionnelle
  - Heure de début et de fin
  - Temps restant pour la tâche en cours (affiché en temps réel).
- Possibilité d’éditer ou de supprimer des tâches.

##### 2.4. **Timer Pomodoro intégré**
- **Cycles de 25 minutes de travail** suivis de **pauses de 5 minutes**.
- **L’écran devient noir** pendant les pauses pour limiter les distractions. L’utilisateur ne peut interagir avec aucune autre fenêtre ou application durant ce temps.
- Affichage d'un compteur de temps indiquant le temps restant pour la tâche en cours et pour la prochaine pause.
- **Pause longue** (15-30 minutes) après 4 cycles de Pomodoro (optionnel).

##### 2.5. **Notification et alerte de début/fin de tâche**
- Notifications ou alertes (sonores et/ou visuelles) à l'approche du début ou de la fin de chaque tâche.
- Notifications similaires pour les débuts et fins des cycles Pomodoro.

##### 2.6. **Mode plein écran**
- L'application passe en mode plein écran pendant chaque cycle Pomodoro et cache toutes les autres fenêtres ou distractions.
- Option pour quitter ce mode avec un raccourci clavier (par exemple `CTRL + Q`).

##### 2.7. **Sauvegarde et historique des tâches**
- L'application enregistre automatiquement les tâches accomplies avec le temps passé sur chacune d'entre elles.
- Un historique des tâches peut être consulté pour visualiser les performances passées (optionnel).

#### 3. **Améliorations possibles**

##### 3.1. **Rapports de productivité**
- Génération de rapports hebdomadaires ou mensuels montrant le temps total passé sur chaque tâche, le nombre de cycles Pomodoro effectués, et des suggestions pour améliorer la productivité.
  
##### 3.2. **Personnalisation avancée du Timer Pomodoro**
- Permettre à l’utilisateur de personnaliser les durées des cycles de travail et de pause selon ses préférences (par exemple, travailler 50 minutes avec une pause de 10 minutes).
- Possibilité de configurer des pauses longues automatiques après un certain nombre de cycles.

##### 3.3. **Intégration avec des outils tiers**
- Synchronisation des tâches avec **Google Calendar**, **Microsoft Outlook** ou d'autres gestionnaires de calendrier pour une meilleure planification.
  
##### 3.4. **Système de priorisation des tâches**
- Implémenter un système de gestion des priorités où les tâches sont classées selon leur importance ou urgence, et l'utilisateur est alerté des tâches urgentes.
  
##### 3.5. **Interface de gestion des tâches**
- Une interface utilisateur pour ajouter, modifier ou supprimer des tâches plus conviviale, avec glisser-déposer pour réorganiser les tâches.
  
##### 3.6. **Mode collaboratif**
- Possibilité de partager des listes de tâches ou d’intégrer un mode collaboratif où plusieurs utilisateurs peuvent contribuer à une même liste de tâches via un réseau local ou cloud.

##### 3.7. **Mode hors-ligne**
- L'application doit fonctionner même sans connexion internet, en sauvegardant les tâches localement.
  
##### 3.8. **Raccourcis clavier et commandes vocales**
- Permettre des **raccourcis clavier** pour ajouter des tâches, lancer ou arrêter le timer Pomodoro rapidement.
- Ajouter une **commande vocale** pour interagir avec l’application.

#### 4. **Contraintes techniques**

##### 4.1. **Compatibilité**
- L’application doit fonctionner sur les systèmes d’exploitation suivants :
  - **Windows 10 et plus**
  - **MacOS**
  - **Linux**
- Il est impératif que l’application fonctionne avec des résolutions d’écran variées sans compromettre la qualité visuelle.

##### 4.2. **Technologies utilisées**
- **Langage** : Python
- **Bibliothèques pour l’interface graphique** : `PyQt`.
- **Timer et gestion du temps** : Python `time`, `schedule` ou `threading` pour la gestion des tâches en temps réel.
- **Notifications** : Bibliothèques comme `Plyer` ou utilisation des API natives du système d'exploitation.
- **Gestion des fichiers** : `JSON` ou `SQLite` pour la sauvegarde des tâches et de l’historique.

##### 4.3. **Performance**
- L’application doit être **légère** et consommer peu de ressources (CPU et RAM).
- Optimisation pour éviter tout ralentissement sur des systèmes moins puissants.

#### 5. **Sécurité et confidentialité**
- Les données de l'utilisateur (tâches, historique) doivent être stockées localement, de préférence dans un dossier sécurisé (dossier utilisateur).
- L’application ne doit pas nécessiter de privilèges d'administration pour son exécution (sauf pour les fonctionnalités liées au démarrage automatique).
  
#### 6. **Livrables attendus**
- **Code source** complet et commenté de l’application.
- **Exécutable** pour les trois systèmes d’exploitation principaux.
- **Documentation utilisateur** expliquant les fonctionnalités, l’installation, et les options de configuration.
- **Tests unitaires** et d’intégration pour les principales fonctionnalités.
- **Documentation développeur** pour permettre une maintenance et des améliorations futures.

#### 7. **Délais et calendrier**
Le projet sera réalisé en **quatre phases** :
- **Phase 1 : Analyse et spécifications détaillées** (1 semaine)
- **Phase 2 : Développement de la version initiale** avec gestion des tâches et Timer Pomodoro (2 à 3 semaines)
- **Phase 3 : Ajout des fonctionnalités avancées et améliorations** (2 semaines)
- **Phase 4 : Tests, correction des bugs et optimisation** (1 semaine)
