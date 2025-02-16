
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,QLineEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog, QMessageBox)
from dialogs import PatientDialog, RecordDialog
from PyQt6.QtGui import *



class PatientsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пациенты")
        self.setGeometry(100, 100, 800, 600)
        self.connection = sqlite3.connect('medical_system.db')

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_patient_input = QLineEdit()
        self.search_patient_input.setPlaceholderText("Поиск пациента (Фамилия)")
        search_layout.addWidget(self.search_patient_input)

        search_button = QPushButton("Поиск")
        search_button.setIcon(QIcon('images/magnifier.png'))
        search_button.clicked.connect(self.search_patient)
        search_layout.addWidget(search_button)

        search_button = QPushButton("")
        search_button.setIcon(QIcon('images/arrow-curve-180-left.png'))
        search_button.clicked.connect(self.load_patients)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        button_layout = QHBoxLayout()
        self.add_patient_button = QPushButton("Добавить пациента")
        self.add_patient_button.clicked.connect(self.add_patient)
        button_layout.addWidget(self.add_patient_button)

        self.delete_patient_button = QPushButton("Удалить пациента")
        self.delete_patient_button.clicked.connect(self.delete_patient)
        button_layout.addWidget(self.delete_patient_button)

        self.update_patient_button = QPushButton("Изменить данные пациента")
        self.update_patient_button.clicked.connect(self.edit_patient)
        button_layout.addWidget(self.update_patient_button)

        layout.addLayout(button_layout)

        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(7)
        self.patient_table.setHorizontalHeaderLabels(
            ["Полис", "Фамилия", "Имя", "Отчество", "Дата рождения", "Пол", "Телефон"]
        )
        layout.addWidget(self.patient_table)

        self.create_record_button = QPushButton("Записать на анализ")
        self.create_record_button.clicked.connect(self.create_record)
        layout.addWidget(self.create_record_button)

        self.view_records_button = QPushButton("Просмотр записей")
        self.view_records_button.clicked.connect(self.view_patient_records)
        layout.addWidget(self.view_records_button)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(5)
        self.record_table.setHorizontalHeaderLabels(["Полис", "Пациент", "Дата", "Время", "Анализ"])
        self.record_table.setVisible(False)
        layout.addWidget(self.record_table)

        self.load_patients()

        layout.addWidget(self.patient_table)
        self.setLayout(layout)

    def load_patients(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Patients")
        rows = cursor.fetchall()
        connection.close()

        self.patient_table.setRowCount(0)
        for row in rows:
            row_position = self.patient_table.rowCount()
            self.patient_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.patient_table.setItem(row_position, column, QTableWidgetItem(str(data)))

        connection.close()

    def search_patient(self):
        cursor = self.connection.cursor()
        search_text = self.search_patient_input.text()
        if search_text:
            cursor.execute('SELECT * FROM Patients WHERE Last_Name = ?', (search_text,))
            data = cursor.fetchall()
            self.patient_table.setRowCount(0)
            if data:
                self.patient_table.setRowCount(len(data))
                for row_index, row_data in enumerate(data):
                    for column_index, column_data in enumerate(row_data):
                        self.patient_table.setItem(row_index, column_index, QTableWidgetItem(str(column_data)))
            else:
                QMessageBox.information(self, "Результат", "Пациенты с этой фамилией не найдены.")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите текст для поиска.")

    def add_patient(self):
        dialog = PatientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()


    def delete_patient(self):
        row = self.patient_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента для удаления.")
            return

        patient_id = self.patient_table.item(row, 0).text()
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Patients WHERE ID_patient = ?", (patient_id,))
        connection.commit()
        connection.close()
        self.load_patients()


    def edit_patient(self):
        row = self.patient_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента для обновления.")
            return

        patient_id = self.patient_table.item(row, 0).text()

        dialog = PatientDialog(self, patient_id=patient_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_patients()


    def view_patient_records(self):
        patient_id = self.patient_table.currentRow()
        if patient_id < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента для обновления.")
            return

        patient_id = self.patient_table.item(patient_id, 0).text()

        if patient_id:
            cursor = self.connection.cursor()
            cursor.execute('''
        SELECT 
            p.ID_patient,
            p.Last_Name || ' ' || SUBSTR(p.First_Name, 1, 1) || '. ' || SUBSTR(p.Middle_Name, 1, 1) || '.' AS Full_Name,
            pr.Date_of_Appointment, 
            pr.Time_of_Appointment, 
            a.Analysis_Name
        FROM 
            Patient_Records pr
        JOIN 
            Patients p ON pr.ID_patient = p.ID_patient
        JOIN 
            Analyses a ON pr.ID_analysis = a.ID_analysis
        WHERE 
            pr.ID_patient = ?
        ''', (patient_id,))
            records = cursor.fetchall()

            self.record_table.setRowCount(0)
            for row_data in records:
                row_position = self.record_table.rowCount()
                self.record_table.insertRow(row_position)
                for col, data in enumerate(row_data):
                    self.record_table.setItem(row_position, col, QTableWidgetItem(str(data)))

            self.record_table.setVisible(True)

    def create_record(self):
        row = self.patient_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пациента для записи на анализ.")
            return

        patient_id = self.patient_table.item(row, 0).text()
        dialog = RecordDialog(self, patient_id=patient_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_records()

    def load_records(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Patient_Records")
        rows = cursor.fetchall()
        connection.close()

        self.record_table.setRowCount(0)
        for row in rows:
            row_position = self.record_table.rowCount()
            self.record_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.record_table.setItem(row_position, column, QTableWidgetItem(str(data)))

        connection.close()