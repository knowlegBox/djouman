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


---
## la partie technique 


### **Partie technique du cahier des charges**

#### 1. **Langages et technologies utilisées**
- **Langage principal** : Python
- **Interface utilisateur (UI)** : Utilisation de **PySide2** pour la création d'une interface graphique moderne, responsive et multi-plateformes.
- **Gestion des tâches et Timer** : Utilisation des modules Python pour la gestion des événements et du temps :
  - **`time`, `threading`** : Gestion des tâches en arrière-plan et exécution des timers (Pomodoro).
  - **`schedule`** : Planification des tâches à des heures spécifiques.

#### 2. **Architecture logicielle**
- **Front-end (Interface utilisateur)** :
  - Composée de fenêtres dynamiques affichant le programme de la journée et les détails des tâches en cours.
  - Fenêtres flottantes pour signaler les tâches et les transitions entre les cycles de travail et les pauses Pomodoro.
  - Timer Pomodoro visible, avec transitions en douceur entre les phases de travail et de pause.

- **Back-end (Gestion des données et logique métier)** :
  - **Gestion des tâches** : Stockage des tâches dans une base de données SQLite.
  - **Sauvegarde locale** : Utilisation de SQLite pour stocker les tâches planifiées et l’historique des tâches réalisées.
  - **Gestion des timers et événements** : Multithreading pour l’exécution parallèle des timers et des événements sans interruption de l’interface utilisateur.
  - **Automatisation du démarrage** : Scripts pour ajouter l’application au démarrage du système (Windows, Linux, MacOS).

#### 3. **Modules Python à utiliser**
- **`PySide2`** : Création de l'interface utilisateur (fenêtres, boutons, labels, etc.).
- **`time`**, **`schedule`**, et **`threading`** : Gestion des tâches en arrière-plan, planification et exécution des timers Pomodoro.
- **`os`** et **`subprocess`** : Gestion du démarrage automatique de l'application.
- **`plyer`** : Notifications système pour avertir l'utilisateur des changements de tâche ou de la fin d'un cycle.
- **`sqlite3`** : Base de données locale pour la gestion des tâches et de l'historique.
- **`playsound` ou `winsound`** : Notifications sonores à la fin de chaque cycle de travail ou pause.

#### 4. **Compatibilité et systèmes d’exploitation**
L’application doit être compatible avec les principaux systèmes d’exploitation :
- **Windows** : Utilisation du registre Windows pour le démarrage automatique et les notifications système.
- **Linux** : Utilisation du fichier `~/.config/autostart` pour démarrer l’application automatiquement.
- **MacOS** : Utilisation du service de démarrage `launchctl` pour l'exécution au démarrage.

#### 5. **Gestion du Timer Pomodoro**
- **Cycles de travail** : 25 minutes de travail suivies de 5 minutes de pause.
- **Écran noir pendant les pauses** : Affichage en plein écran avec un arrière-plan noir pour éviter toute distraction.
  - Mode plein écran géré par `PySide2`, avec des options pour bloquer les interactions avec d’autres applications (capturer la souris et le clavier).
- **Compteur de temps visible** : Affichage en temps réel du timer pour chaque tâche, visible dans l'interface utilisateur.

#### 6. **Sauvegarde et historique**
- **Stockage des tâches** : Les tâches seront enregistrées dans une base de données SQLite.
- **Historique des tâches** : L'historique des tâches terminées sera archivé pour permettre une analyse du temps passé sur chaque tâche et la génération de rapports de productivité.
  - Les colonnes incluront les titres des tâches, descriptions, heures de début/fin et durée totale.

#### 7. **Notifications et alertes**
- **Notifications système** : Utilisation de **`plyer`** pour envoyer des notifications sous forme de pop-ups ou bandeaux.
- **Alertes sonores** : Des sons seront déclenchés pour signaler la fin d’une tâche ou d’un cycle Pomodoro.

#### 8. **Sécurité et gestion des ressources**
- **Optimisation des ressources** : L’application fonctionnera en arrière-plan avec une consommation de mémoire (RAM) et de CPU minimale.
- **Protection des données** : Les données utilisateur (tâches et historique) seront stockées localement dans un dossier sécurisé.

#### 9. **Tests et maintenance**
- **Tests unitaires** pour les fonctionnalités principales (gestion des tâches, timers, notifications, etc.).
- **Tests d’intégration** pour garantir la compatibilité multi-plateformes (Windows, MacOS, Linux).
- Documentation complète du code pour faciliter la maintenance et les futures évolutions.

#### 10. **Extensions et améliorations possibles**
- **Personnalisation des cycles Pomodoro** : Permettre à l'utilisateur de modifier la durée des cycles de travail et des pauses.
- **Intégration avec des services tiers** : Possibilité de synchroniser les tâches avec des applications tierces (ex. Google Calendar).
- **Mode collaboratif** : Partage des tâches et synchronisation du timer Pomodoro avec d’autres utilisateurs.
