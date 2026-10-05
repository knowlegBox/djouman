import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

class JsonStorageService:
    """Service to handle reading and writing the .djouman.json file in a project directory."""
    
    FILE_NAME = "tasks.json"

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.djouman_dir = self.project_path / ".djouman"
        self.file_path = self.djouman_dir / self.FILE_NAME
        
        # Migration automatique de l'ancienne structure
        old_file = self.project_path / ".djouman.json"
        if old_file.exists():
            self.djouman_dir.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                import shutil
                shutil.move(str(old_file), str(self.file_path))
                print(f"📦 Migration de l'ancien fichier vers {self.file_path}")
            else:
                old_file.unlink() # Nettoyage si le nouveau existe déjà
                
        old_instructions = self.project_path / "djouman-instructions.md"
        if old_instructions.exists():
            old_instructions.unlink() # Nettoyage de l'ancien fichier à la racine

    def _get_default_schema(self, project_name: str) -> Dict[str, Any]:
        return {
            "project_name": project_name,
            "tasks": []
        }

    def ensure_file_exists(self, project_name: str = "Nouveau Projet") -> None:
        """Crée le fichier avec le schéma par défaut s'il n'existe pas."""
        self.djouman_dir.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            print(f"📁 Création du fichier de tâches local : {self.file_path}")
            self.write_data(self._get_default_schema(project_name))

    def setup_ai_integration(self) -> None:
        """Met en place les fichiers pour l'automatisation IA (hooks et instructions)."""
        self.djouman_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Création des instructions universelles
        instructions_path = self.djouman_dir / "instructions.md"
        instructions_content = (
            "# Instructions pour l'Assistant IA (Djouman)\n\n"
            "Tu agis en tant que Product Manager. Mon application Djouman se synchronise avec le fichier `.djouman/tasks.json`.\n"
            "Lorsque je te demande d'analyser ce projet :\n"
            "1. Lis le README.md et/ou parcours le code source.\n"
            "2. Découpe le projet en épopées (epics), tâches, et sous-tâches.\n"
            "3. Mets à jour le fichier `.djouman/tasks.json` de façon incrémentale, sans écraser les tâches déjà terminées.\n"
            "4. **RÈGLE CRITIQUE :** Tu dois STRICTEMENT utiliser la structure JSON suivante (qui reflète la base de données SQLite) :\n\n"
            "```json\n"
            "{\n"
            "  \"project_name\": \"Nom du projet\",\n"
            "  \"epics\": [\n"
            "    {\n"
            "      \"epic\": \"Nom de l'épopée (ex: Phase 1 - Fondations)\",\n"
            "      \"tasks\": [\n"
            "        {\n"
            "          \"title\": \"Titre concis de la tâche\",\n"
            "          \"description\": \"Description détaillée technique ou métier\",\n"
            "          \"type\": \"feature\", // Options: feature, bug, refactor, test, doc, hotfix\n"
            "          \"priority\": \"moyen\", // Options: faible, moyen, élevé\n"
            "          \"status\": \"pending\", // Options: pending, in_progress, completed, blocked, cancelled\n"
            "          \"command\": \"commande optionnelle pour exécuter cette tâche\",\n"
            "          \"duration\": 120, // Somme exacte des durées des sous-tâches (en minutes)\n"
            "          \"subtasks\": [\n"
            "            {\n"
            "              \"title\": \"Sous-tâche 1\",\n"
            "              \"status\": \"pending\",\n"
            "              \"duration\": 60 // Durée estimée en minutes par toi (l'IA)\n"
            "            },\n"
            "            {\n"
            "              \"title\": \"Sous-tâche 2\",\n"
            "              \"status\": \"pending\",\n"
            "              \"duration\": 60\n"
            "            }\n"
            "          ]\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "5. Pour chaque sous-tâche, estime de manière réaliste le temps nécessaire en minutes (`duration`).\n"
            "6. La `duration` de la tâche parente DOIT être la somme mathématique exacte des durées de ses sous-tâches.\n"
            "7. Ne génère aucun autre texte d'accompagnement, retourne uniquement le JSON valide."
        )
        
        # Écriture forcée pour mettre à jour les instructions existantes
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(instructions_content)
        print(f"🤖 Mise à jour des instructions IA universelles : {instructions_path}")

        # 2. Création du Skill Antigravity (Raccourci /djouman)
        agents_dir = self.project_path / ".agents"
        skills_dir = agents_dir / "skills" / "djouman"
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        skill_path = skills_dir / "SKILL.md"
        
        skill_content = (
            "---\n"
            "name: djouman\n"
            "description: Analyse le projet pour générer les tâches Djouman\n"
            "---\n"
            "# Initialisation de Djouman\n\n"
            "Lorsque l'utilisateur fait appel à toi via `/djouman`, tu dois :\n"
            "1. Prendre connaissance des règles écrites dans `.djouman/instructions.md`.\n"
            "2. Demander la permission à l'utilisateur : 'Veux-tu que j'analyse ce projet pour générer les tâches pour ce projet ?'\n"
            "3. Si oui, analyse le README et le code, puis mets à jour `.djouman/tasks.json`.\n"
        )
        
        # On force la maj du skill aussi pour être sûr qu'il pointe vers les bons dossiers
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_content)
        print(f"🪄 Mise à jour du raccourci Antigravity (/djouman) : {skill_path}")


    def read_data(self) -> Dict[str, Any]:
        """Lit et retourne le contenu du fichier JSON."""
        if not self.file_path.exists():
            return self._get_default_schema(self.project_path.name)
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON dans {self.file_path}. Fichier potentiellement corrompu.")
            return self._get_default_schema(self.project_path.name)

    def write_data(self, data: Dict[str, Any]) -> None:
        """Écrit les données dans le fichier JSON."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Retourne la liste des tâches."""
        data = self.read_data()
        return data.get("tasks", [])

    def add_task(self, task: Dict[str, Any]) -> None:
        """Ajoute une nouvelle tâche."""
        data = self.read_data()
        if "tasks" not in data:
            data["tasks"] = []
        data["tasks"].append(task)
        self.write_data(data)

    def update_task(self, task_id: str, updated_task: Dict[str, Any]) -> bool:
        """Met à jour une tâche existante. Retourne True si modifiée, False sinon."""
        data = self.read_data()
        tasks = data.get("tasks", [])
        
        for i, t in enumerate(tasks):
            if t.get("id") == task_id:
                tasks[i] = updated_task
                self.write_data(data)
                return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """Supprime une tâche. Retourne True si supprimée, False sinon."""
        data = self.read_data()
        tasks = data.get("tasks", [])
        
        initial_length = len(tasks)
        data["tasks"] = [t for t in tasks if t.get("id") != task_id]
        
        if len(data["tasks"]) < initial_length:
            self.write_data(data)
            return True
        return False
