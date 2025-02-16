import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton)
from PyQt6.QtGui import *
from medworkers import MedworkersWindow
from analyses import AnalysesWindow
from analysis_categories import AnalysisCategoriesWindow
class AdminWindow(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.setWindowTitle("Администрирование клиники")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)
        self.login_window = login_window

        layout = QVBoxLayout()

        self.medworkers_button = QPushButton("Медработники")
        self.medworkers_button.clicked.connect(self.open_medworkers_window)
        layout.addWidget(self.medworkers_button)

        self.analyses_button = QPushButton("Анализы")
        self.analyses_button.clicked.connect(self.open_analyses_window)
        layout.addWidget(self.analyses_button)

        self.analysis_categories_button = QPushButton("Категории анализов")
        self.analysis_categories_button.clicked.connect(self.open_analysis_categories_window)
        layout.addWidget(self.analysis_categories_button)

        self.exit_button = QPushButton("Выйти")
        self.exit_button.setStyleSheet("background-color: #F2F2F2; color: black;")
        self.exit_button.setIcon(QIcon('images/door-open-out.png'))
        self.exit_button.clicked.connect(self.logout)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def open_medworkers_window(self):
        self.medworkers_window = MedworkersWindow()
        self.medworkers_window.show()
    def open_analyses_window(self):
        self.analyses_window = AnalysesWindow()
        self.analyses_window.show()
    def open_analysis_categories_window(self):
        self.analysis_categories_window = AnalysisCategoriesWindow()
        self.analysis_categories_window.show()
    def logout(self):
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())



