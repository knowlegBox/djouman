# MVP : Djuma orienté développeur + extension VS Code

## Objectif
Créer un produit de productivité pour développeurs qui combine :
- un logiciel central de gestion des tâches et du temps,
- et une extension VS Code qui agit comme copilote technique.

L’idée est simple : le logiciel gère le focus, la planification et le suivi de travail, tandis que l’extension apporte le contexte du projet, du code et des tâches techniques.

---

## Vision produit

### Logiciel principal
Le logiciel sert à :
- gérer les tâches quotidiennes,
- suivre le temps passé par tâche,
- gérer les projets et priorités,
- activer le mode focus,
- limiter les distractions,
- afficher un dashboard de productivité.

### Extension VS Code
L’extension sert à :
- détecter le projet actif,
- lier les tâches au repo actuel,
- analyser le contexte de travail du développeur,
- aider à créer, organiser et prioriser les tâches techniques,
- transformer une idée, un bug ou un ticket en tâches exploitables,
- proposer des actions utiles directement depuis l’éditeur.

---

## MVP fonctionnel

### 1. Gestion des tâches techniques
- Créer une tâche avec les champs suivants :
  - titre
  - description
  - type (bug, feature, refactor, test, doc, hotfix)
  - priorité
  - statut
  - projet
  - branche
  - ticket / issue
- Ajouter une vue par projet
- Ajouter une vue par statut : backlog, en cours, bloqué, terminé

### 2. Association projet / repo / branche
- Lier une tâche à un projet Git
- Ajouter le nom du repo associé
- Ajouter le nom de la branche active
- Ajouter un lien vers un ticket externe (GitHub, GitLab, Jira, Azure DevOps)

### 3. Suivi du temps
- Démarrer/arrêter un minuteur pour une tâche
- Enregistrer le temps total par tâche
- Enregistrer le temps par projet
- Afficher le total journalier / hebdomadaire

### 4. Mode Focus développeur
- Bloquer les applications non utiles pendant un session de travail
- Autoriser une liste blanche : IDE, terminal, docs, outils techniques
- Bloquer les distractions : réseaux sociaux, messageries, streaming, sites non pertinents
- Ajouter un statut "en focus" et une pause automatique

### 5. Extension VS Code
- Détecter le workspace ouvert
- Détecter le projet actif et la branche Git
- Afficher les tâches associées au projet
- Créer une tâche à partir du contexte du fichier ouvert
- Résumer un bug ou une feature en tâches
- Proposer une priorisation rapide des tâches

### 6. Assistance IA basique
L’IA dans l’extension peut faire :
- transformer une idée en tâche claire
- décomposer une feature en sous-tâches
- résumer un ticket ou un message de bug
- suggérer la priorité de la tâche
- proposer la prochaine action technique
- organiser les tâches par urgence

---

## Cas d’usage principaux

### Cas 1 : créer une tâche depuis un bug
- L’utilisateur a un bug ou un besoin exprimé
- Il clique sur "Créer tâche depuis le contexte"
- L’extension récupère le projet, le fichier, la branche et le contexte courant
- L’IA génère :
  - titre
  - description
  - type
  - priorité
  - sous-tâches suggérées

### Cas 2 : prioriser le travail du jour
- L’utilisateur ouvre le dashboard
- L’IA classe les tâches par :
  - urgence
  - complexité
  - blocage
  - dépendances
- Le logiciel propose la suite de travail la plus pertinente

### Cas 3 : rester concentré
- L’utilisateur démarre une session focus
- Les apps non autorisées sont bloquées
- La tâche active est affichée
- Il peut soit terminer, soit mettre en pause ou en snooze

### Cas 4 : connecter le travail au projet réel
- Le développeur travaille dans un repo
- La tâche est déjà associée au repo et à la branche
- L’extension propose des actions liées au projet en cours

---

## Fonctionnalités IA prioritaires

### Priorité 1
- Générer une tâche à partir d’une idée ou d’un ticket
- Décomposer une feature en sous-tâches
- Assigner la priorité et le type de tâche
- Proposer une description technique pour la tâche

### Priorité 2
- Analyser le contexte Git du projet
- Lire le fichier actif et la branche courante
- Identifier les tâches liées au contexte actuel
- Aider à clarifier le prochain objectif

### Priorité 3
- Fournir des recommandations de focus
- Analyser le temps passé
- Proposer les tâches à traiter en priorité
- Suggérer les blocages et les interruptions

---

## Architecture cible

### Couche 1 : Logiciel principal
- interface utilisateur
- gestion des tâches
- suivi du temps
- mode focus
- dashboard

### Couche 2 : Extension VS Code
- intégration au workspace
- accès au repo et à la branche
- extraction du contexte technique
- génération de tâches assistées par IA

### Couche 3 : IA / moteur intelligent
- génération de description de tâches
- classification
- priorisation
- résumé
- recommandations de productivité

### Couche 4 : intégrations externes
- GitHub
- GitLab
- Jira
- Azure DevOps

---

## MVP “minimum viable product” à lancer

- [ ] Tâches techniques avec type, statut et priorité
- [ ] Projet + repo + branche + ticket
- [ ] Minuteur de tâche
- [ ] Dashboard simple
- [ ] Mode focus développeur
- [ ] Extension VS Code de base
- [ ] IA pour générer et structurer les tâches
- [ ] Vue par projet et par statut

---

## Ce qui fait la différence

Le vrai avantage de ce MVP n’est pas seulement d’avoir une IA. C’est d’avoir une IA intégrée dans le vrai environnement du développeur :
- son code
- son projet
- son repo
- sa branche
- ses tâches
- son flux de travail

C’est ce qui transforme l’outil d’un simple gestionnaire de tâches en un assistant de productivité technique réel.

---

## Conclusion

Le meilleur MVP pour ce produit est un mélange de :
- logiciel central de gestion du temps et du focus,
- extension VS Code comme copilote technique,
- IA pour aider à créer, organiser, prioriser et suivre les tâches.

C’est une direction forte, cohérente et bien alignée avec les besoins des développeurs.
