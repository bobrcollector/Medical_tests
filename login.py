import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QVBoxLayout, QWidget)
from main_admin import AdminWindow
from main_worker import WorkWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 150)
        self.setFixedSize(300, 150)
        self.label_login = QLabel("Логин")
        self.input_login = QLineEdit()

        self.label_passwd = QLabel("Пароль:")
        self.input_passwd = QLineEdit()
        self.input_passwd.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_login = QPushButton("Войти")
        self.button_login.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_login)
        layout.addWidget(self.input_login)
        layout.addWidget(self.label_passwd)
        layout.addWidget(self.input_passwd)
        layout.addWidget(self.button_login)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.connection = sqlite3.connect('medical_system.db')
        self.cursor = self.connection.cursor()
        self.logged_in_medworker_id = None

    def login(self):
        login = self.input_login.text()
        password = self.input_passwd.text()

        if login == "admin" and password == "admin":
            self.open_admin_window()
        else:
            self.cursor.execute("SELECT ID_medworker FROM Medworkers WHERE Login = ? AND Passwd = ?",
                                (login, password))
            result = self.cursor.fetchone()
            if result:
                self.logged_in_medworker_id = result[0]
                self.open_work_window()
            else:
                QMessageBox.warning(self, "Error", "Неправильно введен логин или пароль")

    def open_work_window(self):
        self.work_window = WorkWindow(self, self.logged_in_medworker_id)
        self.work_window.show()
        self.close()

    def open_admin_window(self):
        self.admin_window = AdminWindow(self)
        self.admin_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
