import sqlite3
from typing import List, Tuple


class DbHandler:
    def __init__(self, my_task=None):
        # self.connexion = None
        self.db_creation()
        self.cursor = self.connexion.cursor()

    def db_creation(self) -> None:
        self.connexion = sqlite3.connect('task.db')
        self.connexion.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            duration INTEGER NOT NULL,
            priority INTEGER NOT NULL
        )""")
        self.connexion.commit()

    def add_row(self, data: tuple[str, int, int]) -> bool:
        try:
            self.cursor.execute('INSERT INTO tasks( description,duration, priority) VALUES(?,?,?)',
                                data
                                )
            if self.cursor.rowcount > 0:
                print('valider')
                self.connexion.commit()
                return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'enregistrement {e}")
            return False

    def show_rows(self) -> List[tuple[int, str, int, int]]:
        try:
            data = self.connexion.execute('SELECT * FROM tasks')
            rows = data.fetchall()
            print(f'vous avez {len(rows)} tâche(s)')
            return rows
        except sqlite3.Error as e:
            print('La recupération de donné a échoué', e)
            return []

    def delete_row(self, task_id: int) -> bool:
        try:
            self.cursor.execute('DELETE FROM task WHERE id=?', (task_id,))
            if self.cursor.rowcount():
                print('La tâche à bien été supprimée')
                return True
            else:
                print('Echec lors de la suppression de la tâche')
                return False

        except sqlite3.Error as e:
            print(f'Erreur lors de la suppression de la tâche {e}')
            return False

    def __del__(self):
        """Ferme la connexion à la base de données lors de la destruction de l'objet."""
        if self.connexion:
            self.connexion.close()


def how_to() -> None:
    print(' Creer une tache avec la "description","durée(min)" et la "priorité" separer par une virgule')
    print('1- Maintenant, 2- Demain, 3- Plus tard')


def user_task() -> tuple[str, int, int]:
    usertask = input('Entrer votre tache : ')
    task = usertask.split(',')

    if len(task) != 3 or not task[1].strip().isdigit() or not task[2].strip().isdigit():
        print('Entrez une tâche valide')
        user_task()
    else:
        return task[0].strip(), int(task[1].strip()), int(task[2].strip())


if __name__ == '__main__':
    # how_to()
    # task = user_task()
    task = DbHandler()
    all_task = task.show_rows()


