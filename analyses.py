import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog, QMessageBox
)
from dialogs import AnalysesDialog
from PyQt6.QtGui import *


class AnalysesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализы")
        self.setGeometry(100, 100, 800, 600)
        self.connection = sqlite3.connect('medical_system.db')

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_analyses_input = QLineEdit()
        self.search_analyses_input.setPlaceholderText("Поиск анализа")
        search_layout.addWidget(self.search_analyses_input)

        search_button = QPushButton("Поиск")
        search_button.setIcon(QIcon('magnifier.png'))
        search_button.clicked.connect(self.search_analyses)
        search_layout.addWidget(search_button)

        search_button = QPushButton("")
        search_button.setIcon(QIcon('images/arrow-curve-180-left.png'))
        search_button.clicked.connect(self.load_analyses)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        button_layout = QHBoxLayout()
        self.add_analyses_button = QPushButton("Добавить анализ")
        self.add_analyses_button.clicked.connect(self.add_analyses)
        button_layout.addWidget(self.add_analyses_button)

        self.delete_analyses_button = QPushButton("Удалить анализ")
        self.delete_analyses_button.clicked.connect(self.delete_analyses)
        button_layout.addWidget(self.delete_analyses_button)

        self.update_analyses_button = QPushButton("Изменить информацию анализа")
        self.update_analyses_button.clicked.connect(self.edit_analyses)
        button_layout.addWidget(self.update_analyses_button)

        layout.addLayout(button_layout)

        self.analyses_table = QTableWidget()
        self.analyses_table.setColumnCount(3)
        self.analyses_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Категория"]
        )
        layout.addWidget(self.analyses_table)

        self.load_analyses()

        layout.addWidget(self.analyses_table)
        self.setLayout(layout)

    def load_analyses(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute('''    SELECT a.ID_analysis, a.Analysis_Name, ac.Category_Name
    FROM Analyses a
    JOIN Analysis_Categories ac ON a.ID_analysis_category = ac.ID_analysis_category
    ORDER BY ac.Category_Name, a.Analysis_Name
                ''')
        rows = cursor.fetchall()
        connection.close()

        self.analyses_table.setRowCount(0)
        for row in rows:
            row_position = self.analyses_table.rowCount()
            self.analyses_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.analyses_table.setItem(row_position, column, QTableWidgetItem(str(data)))

        connection.close()

    def search_analyses(self):
        cursor = self.connection.cursor()
        search_text = self.search_analyses_input.text()
        if search_text:
            cursor.execute('''SELECT a.ID_analysis, a.Analysis_Name, ac.Category_Name
                 FROM Analyses a
                 JOIN Analysis_Categories ac ON a.ID_analysis_category = ac.ID_analysis_category
                 WHERE Analysis_Name = ?
                 ORDER BY ac.Category_Name, a.Analysis_Name''', (search_text,))
            data = cursor.fetchall()
            self.analyses_table.setRowCount(0)
            if data:
                self.analyses_table.setRowCount(len(data))
                for row_index, row_data in enumerate(data):
                    for column_index, column_data in enumerate(row_data):
                        self.analyses_table.setItem(row_index, column_index, QTableWidgetItem(str(column_data)))
            else:
                QMessageBox.information(self, "Результат", "Анализ с таким названием не найден")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите текст для поиска.")

    def add_analyses(self):
        dialog = AnalysesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_analyses()

    def delete_analyses(self):
        row = self.analyses_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите анализ для удаления.")
            return

        analyses_id = self.analyses_table.item(row, 0).text()
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Analyses WHERE ID_analysis = ?", (analyses_id,))
        connection.commit()
        connection.close()
        self.load_analyses()

    def edit_analyses(self):
        row = self.analyses_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите анализ для изменения.")
            return

        analyses_id = self.analyses_table.item(row, 0).text()

        try:
            dialog = AnalysesDialog(self, analyses_id=analyses_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_analyses()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии диалогового окна: {str(e)}")

