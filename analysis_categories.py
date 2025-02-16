import sys
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDialog, QHBoxLayout)
from dialogs import AnalysisCategoryDialog


class AnalysisCategoriesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Категории анализов")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить категорию")
        self.delete_button = QPushButton("Удалить категорию")
        self.edit_button = QPushButton("Изменить информацию об категории")

        self.add_button.clicked.connect(self.add_analysis_categories)
        self.delete_button.clicked.connect(self.delete_analysis_categories)
        self.edit_button.clicked.connect(self.edit_analysis_categories)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.edit_button)

        layout.addLayout(button_layout)

        self.analysis_categories_table = QTableWidget()
        self.analysis_categories_table.setColumnCount(2)
        self.analysis_categories_table.setHorizontalHeaderLabels(["ID", "Название категории"])
        self.analysis_categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.load_analysis_categories()

        layout.addWidget(self.analysis_categories_table)
        self.setLayout(layout)

    def load_analysis_categories(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Analysis_Categories")
        rows = cursor.fetchall()
        self.analysis_categories_table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                self.analysis_categories_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

        connection.close()

    def add_analysis_categories(self):
        dialog = AnalysisCategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_analysis_categories()

    def delete_analysis_categories(self):
        row = self.analysis_categories_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите медработника для удаления.")
            return

        analysis_categories_id = self.analysis_categories_table.item(row, 0).text()
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Analysis_Categories WHERE ID_analysis_category = ?", (analysis_categories_id,))
        connection.commit()
        connection.close()
        self.load_analysis_categories()

    def edit_analysis_categories(self):
        row = self.analysis_categories_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для изменения.")
            return

        analysis_categories_id = self.analysis_categories_table.item(row, 0).text()

        try:
            dialog = AnalysisCategoryDialog(self, analysis_categories_id=analysis_categories_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_analysis_categories()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии диалогового окна: {str(e)}")
