# import time
#
# from PySide6 import QtWidgets, QtCore
# from PySide6.QtCore import QTimer
# from PySide6.QtWidgets import QApplication, QWidget
#
#
# class BlackScreen(QWidget):
#     def __init__(self, duration: int = 300):
#         super().__init__()
#         self.showFullScreen()
#         self.setStyleSheet("background-color: #333;")
#         self.launcher()
#         self.durations = duration
#         self.start_timer()
#
#     def launcher(self) -> None:
#         self.my_layout()
#         self.add_to_layout()
#         self.set_my_layout()
#
#     def my_layout(self) -> None:
#         self.vbox_layout = QtWidgets.QVBoxLayout()
#
#     def add_to_layout(self) -> None:
#         self.label = QtWidgets.QLabel(self.format_time(self.durations), self)
#         self.label.setStyleSheet("""
#         color:white;
#         text-align:center;
#         font-size:72px;
#         border: 2px solid white;
#         """)
#         self.label.setAlignment(QtCore.Qt.AlignCenter)
#         self.vbox_layout.addWidget(self.label)
#
#     def set_my_layout(self) -> None:
#         self.setLayout(self.vbox_layout)
#
#     def start_timer(self):
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_countdown)
#         self.timer.start(1000)
#
#     def update_countdown(self)->None:
#         if self.durations > 0:
#             self.durations -= 1
#             self.label.setText(self.format_time(self.durations))
#         else:
#             self.timer.stop()
#             self.label.setText("Temps écoulé ! 🚨")
#             self.label.setStyleSheet("color: red; font-size: 48px; text-align: center;")
#
#     @staticmethod
#     def format_time(seconds: int) -> str:
#         mins, secs = divmod(seconds, 60)
#         return f"{min:02}:{secs:02}"
#
#
# if __name__ == '__main__':
#     app = QApplication([])
#     win = BlackScreen()
#     win.show()
#     app.exec()
#     # decompteur(45)
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget


class BlackScreen(QWidget):
    def __init__(self, duration: int = 300):
        super().__init__()
        self.setWindowTitle("Compte à rebours")
        self.setStyleSheet("background-color: #333;")
        self.showFullScreen()

        self.duration = duration  # Temps total en secondes
        self.init_ui()
        self.start_timer()

    def init_ui(self):
        """Initialise l'interface utilisateur et le layout."""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Label pour afficher le compte à rebours
        self.label = QtWidgets.QLabel(self.format_time(self.duration), self)
        self.label.setStyleSheet("""
            color: white;
            text-align: center;
            font-size: 72px;
            border: 2px solid white;
        """)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def start_timer(self):
        """Démarre le QTimer pour le compte à rebours."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)  # Lier l'événement timeout
        self.timer.start(1000)  # Déclenchement toutes les 1000 ms (1 seconde)

    def update_countdown(self):
        """Met à jour le temps restant chaque seconde."""
        if self.duration > 0:
            self.duration -= 1
            self.label.setText(self.format_time(self.duration))
        else:
            self.timer.stop()
            self.label.setText("Temps écoulé ! 🚨")
            self.label.setStyleSheet("color: red; font-size: 48px; text-align: center;")

    @staticmethod
    def format_time(seconds: int) -> str:
        """Formate le temps en minutes et secondes (MM:SS)."""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"


if __name__ == '__main__':
    app = QApplication([])
    win = BlackScreen()  # Exemple : compte à rebours de 10 secondes
    win.show()
    app.exec()
