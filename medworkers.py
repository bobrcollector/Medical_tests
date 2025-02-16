
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog, QMessageBox)
from dialogs import MedworkerDialog
from PyQt6.QtGui import *



class MedworkersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Медработники")
        self.setGeometry(100, 100, 800, 600)
        self.connection = sqlite3.connect('medical_system.db')

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_medworker_input = QLineEdit()
        self.search_medworker_input.setPlaceholderText("Поиск медицинского работника (ФИО)")
        search_layout.addWidget(self.search_medworker_input)

        search_button = QPushButton("Поиск")
        search_button.setIcon(QIcon('images/magnifier.png'))
        search_button.clicked.connect(self.search_medworker)
        search_layout.addWidget(search_button)

        search_button = QPushButton("")
        search_button.setIcon(QIcon('images/arrow-curve-180-left.png'))
        search_button.clicked.connect(self.load_medworkers)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        button_layout = QHBoxLayout()
        self.add_medworker_button = QPushButton("Добавить медработника")
        self.add_medworker_button.clicked.connect(self.add_medworker)
        button_layout.addWidget(self.add_medworker_button)

        self.delete_medworker_button = QPushButton("Удалить медработника")
        self.delete_medworker_button.clicked.connect(self.delete_medworker)
        button_layout.addWidget(self.delete_medworker_button)

        self.update_medworker_button = QPushButton("Изменить данные медработника")
        self.update_medworker_button.clicked.connect(self.edit_medworker)
        button_layout.addWidget(self.update_medworker_button)

        layout.addLayout(button_layout)

        self.medworker_table = QTableWidget()
        self.medworker_table.setColumnCount(6)
        self.medworker_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Логин", "Пароль"]
        )
        layout.addWidget(self.medworker_table)

        self.view_records_button = QPushButton("Просмотр выполненных анализов")
        self.view_records_button.clicked.connect(self.view_medworker_records)
        layout.addWidget(self.view_records_button)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(4)
        self.record_table.setHorizontalHeaderLabels(["Номер записи", "Пациент", "Дата", "Результат"])
        self.record_table.setVisible(False)
        layout.addWidget(self.record_table)

        self.load_medworkers()

        layout.addWidget(self.medworker_table)
        self.setLayout(layout)

    def load_medworkers(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Medworkers")
        rows = cursor.fetchall()
        connection.close()

        self.medworker_table.setRowCount(0)
        for row in rows:
            row_position = self.medworker_table.rowCount()
            self.medworker_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.medworker_table.setItem(row_position, column, QTableWidgetItem(str(data)))

        connection.close()

    def search_medworker(self):
        cursor = self.connection.cursor()
        search_text = self.search_medworker_input.text()
        if search_text:
            cursor.execute('SELECT * FROM Medworkers WHERE Last_Name = ?', (search_text,))
            data = cursor.fetchall()
            self.medworker_table.setRowCount(0)
            if data:
                self.medworker_table.setRowCount(len(data))
                for row_index, row_data in enumerate(data):
                    for column_index, column_data in enumerate(row_data):
                        self.medworker_table.setItem(row_index, column_index, QTableWidgetItem(str(column_data)))
            else:
                QMessageBox.information(self, "Результат", "Медицинские работники с этой фамилией не найдены.")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите текст для поиска.")

    def add_medworker(self):
        dialog = MedworkerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_medworkers()


    def delete_medworker(self):
        row = self.medworker_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите медработника для удаления.")
            return

        medworker_id = self.medworker_table.item(row, 0).text()
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Medworkers WHERE ID_medworker = ?", (medworker_id,))
        connection.commit()
        connection.close()
        self.load_medworkers()


    def edit_medworker(self):
        row = self.medworker_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите медработника для обновления.")
            return

        medworker_id = self.medworker_table.item(row, 0).text()

        dialog = MedworkerDialog(self, medworker_id=medworker_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_medworkers()


    def view_medworker_records(self):
        medworker_id = self.medworker_table.currentRow()
        if medworker_id < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите медработника для просмотра выполненных им анализов.")
            return

        medworker_id = self.medworker_table.item(medworker_id, 0).text()

        if medworker_id:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT ar.ID_result, 
                       (p.Last_Name || ' ' || SUBSTR(p.First_Name, 1, 1) || '. ' || SUBSTR(p.Middle_Name, 1, 1) || '.') AS Patient_Info, 
                       ar.Date_of_Result, 
                       ar.Result
                FROM Analysis_Results ar
                JOIN Patient_Records pr ON ar.ID_record = pr.ID_record
                JOIN Patients p ON pr.ID_patient = p.ID_patient
                WHERE ar.ID_medworker = ?
                ''', (medworker_id,))
            records = cursor.fetchall()

            self.record_table.setRowCount(0)
            for row_data in records:
                row_position = self.record_table.rowCount()
                self.record_table.insertRow(row_position)
                for col, data in enumerate(row_data):
                    self.record_table.setItem(row_position, col, QTableWidgetItem(str(data)))

            self.record_table.setVisible(True)