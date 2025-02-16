import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel)
from PyQt6.QtGui import *
from patients import PatientsWindow
from records import RecordsWindow

class WorkWindow(QWidget):
    def __init__(self, login_window, medworker_id):
        super().__init__()
        self.setWindowTitle("Окно медицинского работника")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)
        self.login_window = login_window
        self.medworker_id = medworker_id

        layout = QVBoxLayout()

        self.label_medworker = QLabel()
        self.set_medworker_label()
        layout.addWidget(self.label_medworker)

        self.patients_button = QPushButton("Пациенты")
        self.patients_button.clicked.connect(self.open_patients_window)
        layout.addWidget(self.patients_button)

        self.analyses_button = QPushButton("Записи на анализы")
        self.analyses_button.clicked.connect(self.open_records_window)
        layout.addWidget(self.analyses_button)

        self.exit_button = QPushButton("Выйти")
        self.exit_button.setStyleSheet("background-color: #F2F2F2; color: black;")
        self.exit_button.setIcon(QIcon('images/door-open-out.png'))
        self.exit_button.clicked.connect(self.logout)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def set_medworker_label(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT First_Name, Last_Name FROM Medworkers WHERE ID_medworker = ?", (self.medworker_id,))
        result = cursor.fetchone()
        connection.close()
        if result:
            self.label_medworker.setText(f"Авторизован: {result[0]} {result[1]}")

    def open_patients_window(self):
        self.patients_window = PatientsWindow()
        self.patients_window.show()

    def open_records_window(self):
        self.records_window = RecordsWindow(self.medworker_id)
        self.records_window.show()

    def logout(self):
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkWindow(None, None)
    window.show()
    sys.exit(app.exec())
