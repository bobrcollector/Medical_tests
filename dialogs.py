import sqlite3
from PyQt6.QtWidgets import (QPushButton, QLineEdit, QMessageBox, QLabel, QDialog,
                             QFormLayout, QComboBox, QCalendarWidget)
from PyQt6.QtCore import QDate
import re


def capitalize_words(input_str):
    return ' '.join(word.capitalize() for word in input_str.split())


def contains_digits(input_str):
    return any(char.isdigit() for char in input_str)


def validate_date(date):
    return re.match(r'^\d{2}\.\d{2}\.\d{4}$', date) is not None


def validate_time(time):
    return re.match(r'^\d{2}:\d{2}$', time) is not None


def validate_phone(phone):
    return re.match(r'^\+?\d{7,15}$', phone) is not None


class PatientDialog(QDialog):
    def __init__(self, parent, patient_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение пациента")
        self.setGeometry(100, 100, 300, 300)

        self.layout = QFormLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()

        self.dob_label = QLabel("Дата рождения:")
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Мужской", "Женский"])
        self.contact_phone_input = QLineEdit()

        if patient_id:
            self.patient_id = patient_id
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Patients WHERE ID_patient = ?", (patient_id,))
            patient = cursor.fetchone()
            connection.close()
            if patient:
                self.last_name_input.setText(patient[1])
                self.first_name_input.setText(patient[2])
                self.middle_name_input.setText(patient[3])

                dob = QDate.fromString(patient[4], "dd.MM.yyyy")
                self.calendar.setSelectedDate(dob)

                self.gender_input.setCurrentText(patient[5])
                self.contact_phone_input.setText(patient[6])

        self.layout.addRow("Фамилия:", self.last_name_input)
        self.layout.addRow("Имя:", self.first_name_input)
        self.layout.addRow("Отчество:", self.middle_name_input)
        self.layout.addRow("Пол:", self.gender_input)
        self.layout.addRow(self.dob_label)
        self.layout.addRow(self.calendar)
        self.layout.addRow("Телефон:", self.contact_phone_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_patient)
        self.layout.addRow(self.save_button)

        self.setLayout(self.layout)

    def save_patient(self):
        first_name = capitalize_words(self.first_name_input.text().strip())
        last_name = capitalize_words(self.last_name_input.text().strip())
        middle_name = capitalize_words(self.middle_name_input.text().strip())

        dob = self.calendar.selectedDate().toString("dd.MM.yyyy")

        contact_phone = self.contact_phone_input.text().strip()

        if not first_name or not last_name or not middle_name or not dob or not contact_phone:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if not validate_phone(contact_phone):
            QMessageBox.warning(self, "Ошибка", "Неверный формат номера телефона! Используйте +712345678.")
            return

        if contains_digits(first_name) or contains_digits(last_name) or contains_digits(middle_name):
            QMessageBox.warning(self, "Ошибка", "ФИО не должно содержать цифр!")
            return

        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        if hasattr(self, 'patient_id') and self.patient_id:
            cursor.execute(
                "UPDATE Patients SET First_Name=?, Last_Name=?, Middle_Name=?, Date_of_Birth=?, Gender=?, Contact_Phone=? WHERE ID_patient=?",
                (first_name, last_name, middle_name, dob, self.gender_input.currentText(), contact_phone,
                 self.patient_id))
        else:
            cursor.execute(
                "INSERT INTO Patients (First_Name, Last_Name, Middle_Name, Date_of_Birth, Gender, Contact_Phone) VALUES (?, ?, ?, ?, ?, ?)",
                (first_name, last_name, middle_name, dob, self.gender_input.currentText(), contact_phone))

        connection.commit()
        connection.close()
        self.accept()


from PyQt6.QtWidgets import QDialog, QFormLayout, QLabel, QCalendarWidget, QTimeEdit, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import QDate, QTime
import sqlite3

class RecordDialog(QDialog):
    def __init__(self, parent, patient_id=None, record_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение записи о пациенте")
        self.setGeometry(100, 100, 300, 300)
        self.layout = QFormLayout()

        self.date_of_appointment_label = QLabel("Дата приема:")
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.time_of_appointment_input = QTimeEdit()
        self.time_of_appointment_input.setDisplayFormat("HH:mm")

        self.patient_selector = QComboBox()
        self.analysis_selector = QComboBox()

        self.load_patients()
        self.load_analyses()

        if patient_id:
            self.patient_selector.setCurrentIndex(self.patient_selector.findData(patient_id))

        if record_id:
            self.record_id = record_id
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Patient_Records WHERE ID_record = ?", (record_id,))
            record = cursor.fetchone()
            connection.close()
            if record:
                date = QDate.fromString(record[2], "dd.MM.yyyy")
                self.calendar.setSelectedDate(date)
                time = QTime.fromString(record[3], "HH:mm")
                self.time_of_appointment_input.setTime(time)
                self.patient_selector.setCurrentIndex(self.patient_selector.findData(record[1]))
                self.analysis_selector.setCurrentIndex(self.analysis_selector.findData(record[4]))

        self.layout.addRow(self.date_of_appointment_label)
        self.layout.addRow(self.calendar)
        self.layout.addRow("Время назначения:", self.time_of_appointment_input)
        self.layout.addRow("Пациент:", self.patient_selector)
        self.layout.addRow("Анализ:", self.analysis_selector)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_record)
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def load_patients(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ID_patient, First_Name || ' ' || Last_Name AS name FROM Patients")
        patients = cursor.fetchall()
        connection.close()
        self.patient_selector.addItem("", "")
        for patient in patients:
            self.patient_selector.addItem(patient[1], patient[0])

    def load_analyses(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ID_analysis, Analysis_Name FROM Analyses")
        analyses = cursor.fetchall()
        connection.close()
        self.analysis_selector.addItem("", "")
        for analysis in analyses:
            self.analysis_selector.addItem(analysis[1], analysis[0])

    def save_record(self):
        date_of_appointment = self.calendar.selectedDate().toString("dd.MM.yyyy")
        time_of_appointment = self.time_of_appointment_input.time().toString("HH:mm")
        patient_id = self.patient_selector.currentData()
        analysis_id = self.analysis_selector.currentData()

        if not date_of_appointment or not time_of_appointment or not patient_id or not analysis_id:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()

        if hasattr(self, 'record_id') and self.record_id:
            cursor.execute(
                "UPDATE Patient_Records SET Date_of_Appointment=?, Time_of_Appointment=?, ID_patient=?, ID_analysis=? WHERE ID_record=?",
                (date_of_appointment, time_of_appointment, patient_id, analysis_id, self.record_id))
        else:
            cursor.execute(
                "INSERT INTO Patient_Records (Date_of_Appointment, Time_of_Appointment, ID_patient, ID_analysis) VALUES (?, ?, ?, ?)",
                (date_of_appointment, time_of_appointment, patient_id, analysis_id))

        connection.commit()
        connection.close()
        self.accept()

class MedworkerDialog(QDialog):
    def __init__(self, parent, medworker_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение медработника")
        self.setGeometry(100, 100, 300, 300)
        self.layout = QFormLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.login_input = QLineEdit()
        self.passwd_input = QLineEdit()

        if medworker_id:
            self.medworker_id = medworker_id
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Medworkers WHERE ID_medworker = ?", (medworker_id,))
            medworker = cursor.fetchone()
            connection.close()
            if medworker:
                self.last_name_input.setText(medworker[1])
                self.first_name_input.setText(medworker[2])
                self.middle_name_input.setText(medworker[3])
                self.login_input.setText(medworker[4])
                self.passwd_input.setText(medworker[5])

        self.layout.addRow("Фамилия:", self.last_name_input)
        self.layout.addRow("Имя:", self.first_name_input)
        self.layout.addRow("Отчество:", self.middle_name_input)
        self.layout.addRow("Логин:", self.login_input)
        self.layout.addRow("Пароль:", self.passwd_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_medworker)
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def save_medworker(self):
        first_name = capitalize_words(self.first_name_input.text().strip())
        last_name = capitalize_words(self.last_name_input.text().strip())
        middle_name = capitalize_words(self.middle_name_input.text().strip())
        login = self.login_input.text()
        passwd = self.passwd_input.text()

        if not first_name or not last_name or not middle_name or not login or not passwd:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if contains_digits(first_name) or contains_digits(last_name) or contains_digits(middle_name):
            QMessageBox.warning(self, "Ошибка", "ФИО не должно содержать цифр!")
            return

        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        if hasattr(self, 'medworker_id') and self.medworker_id:
            cursor.execute(
                "UPDATE Medworkers SET First_Name=?, Last_Name=?, Middle_Name=?, Login=?, Passwd=? WHERE ID_medworker=?",
                (first_name, last_name, middle_name, login, passwd, self.medworker_id))
        else:
            cursor.execute(
                "INSERT INTO Medworkers (First_Name, Last_Name, Middle_Name, Login, Passwd) VALUES (?, ?, ?, ?, ?)",
                (first_name, last_name, middle_name, login, passwd))

        connection.commit()
        connection.close()
        self.accept()


class AnalysisCategoryDialog(QDialog):
    def __init__(self, parent, analysis_categories_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение категории анализа")
        self.setGeometry(100, 100, 300, 150)
        self.layout = QFormLayout()

        self.category_name_input = QLineEdit()
        self.analysis_categories_id = analysis_categories_id

        if analysis_categories_id:
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Analysis_Categories WHERE ID_analysis_category = ?",
                           (analysis_categories_id,))
            category = cursor.fetchone()
            connection.close()
            if category:
                self.category_name_input.setText(category[1])

        self.layout.addRow("Название категории:", self.category_name_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_category)
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def save_category(self):
        category_name = capitalize_words(self.category_name_input.text())

        if not category_name:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if contains_digits(category_name):
            QMessageBox.warning(self, "Ошибка", "Название не должно содержать цифр!")
            return

        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        if self.analysis_categories_id:
            cursor.execute(
                "UPDATE Analysis_Categories SET Category_Name=? WHERE ID_analysis_category=?",
                (category_name, self.analysis_categories_id))
        else:
            cursor.execute(
                "INSERT INTO Analysis_Categories (Category_Name) VALUES (?)",
                (category_name,))

        connection.commit()
        connection.close()
        self.accept()


class AnalysesDialog(QDialog):
    def __init__(self, parent, analyses_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение анализа")
        self.setGeometry(100, 100, 300, 150)

        self.layout = QFormLayout()
        self.analysis_name_input = QLineEdit()
        self.analysis_category_selector = QComboBox()

        self.load_analysis_category()

        if analyses_id:
            self.analyses_id = analyses_id
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Analyses WHERE ID_analysis = ?", (analyses_id,))
            analyses = cursor.fetchone()
            connection.close()
            if analyses:
                self.analysis_name_input.setText(analyses[1])
                self.analysis_category_selector.setCurrentIndex(
                    self.analysis_category_selector.findData(analyses[2])
                )

        self.layout.addRow("Название анализа:", self.analysis_name_input)
        self.layout.addRow("Категория анализа:", self.analysis_category_selector)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_analyses)
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def load_analysis_category(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ID_analysis_category, Category_Name FROM Analysis_Categories")
        analysis_categories = cursor.fetchall()
        connection.close()

        self.analysis_category_selector.addItem("Выберите категорию", "")
        for category in analysis_categories:
            self.analysis_category_selector.addItem(category[1], category[0])

    def save_analyses(self):
        analysis_name = capitalize_words(self.analysis_name_input.text())
        selected_category_id = self.analysis_category_selector.currentData()

        if not analysis_name or not selected_category_id:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if contains_digits(analysis_name):
            QMessageBox.warning(self, "Ошибка", "Название не должно содержать цифр!")
            return
        try:
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()

            if hasattr(self, 'analyses_id') and self.analyses_id:
                cursor.execute(
                    "UPDATE Analyses SET Analysis_Name=?, ID_analysis_category=? WHERE ID_analysis=?",
                    (analysis_name, selected_category_id, self.analyses_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO Analyses (Analysis_Name, ID_analysis_category) VALUES (?, ?)",
                    (analysis_name, selected_category_id)
                )

            connection.commit()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения данных: {str(e)}")
        finally:
            connection.close()

        self.accept()


class AnalysisResultDialog(QDialog):
    def __init__(self, parent, medworker_id, record_id=None, result_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление/Изменение результата анализа")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QFormLayout()

        self.date_of_result_label = QLabel("Дата получения результата:")
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)

        self.result_input = QLineEdit()
        self.record_selector = QComboBox()
        self.medworker_selector = QComboBox()

        self.load_records()
        self.load_medworkers()

        if self.medworker_selector.findData(medworker_id) != -1:
            self.medworker_selector.setCurrentIndex(self.medworker_selector.findData(medworker_id))
            self.medworker_selector.setDisabled(True)

        if record_id:
            self.record_selector.setCurrentIndex(self.record_selector.findData(record_id))
            self.record_selector.setDisabled(True)  # Отключаем возможность изменения записи

        if result_id:
            self.result_id = result_id
            connection = sqlite3.connect('medical_system.db')
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Analysis_Results WHERE ID_result = ?", (result_id,))
            result = cursor.fetchone()
            connection.close()
            if result:
                date = QDate.fromString(result[2], "dd.MM.yyyy")
                self.calendar.setSelectedDate(date)
                self.result_input.setText(str(result[4]))
                self.record_selector.setCurrentIndex(self.record_selector.findData(result[1]))
                self.medworker_selector.setCurrentIndex(self.medworker_selector.findData(result[2]))

        self.layout.addRow(self.date_of_result_label)
        self.layout.addRow(self.calendar)
        self.layout.addRow("Результат:", self.result_input)
        self.layout.addRow("Запись пациента:", self.record_selector)
        self.layout.addRow("Сотрудник:", self.medworker_selector)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_result)
        self.layout.addRow(self.save_button)
        self.setLayout(self.layout)

    def load_records(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ID_record, Date_of_Appointment FROM Patient_Records")
        records = cursor.fetchall()
        connection.close()
        self.record_selector.addItem("", "")
        for record in records:
            self.record_selector.addItem(f"Запись {record[0]} - {record[1]}", record[0])

    def load_medworkers(self):
        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ID_medworker, First_Name || ' ' || Last_Name AS name FROM Medworkers")
        medworkers = cursor.fetchall()
        connection.close()
        self.medworker_selector.addItem("", "")
        for medworker in medworkers:
            self.medworker_selector.addItem(medworker[1], medworker[0])

    def save_result(self):
        date_of_result = self.calendar.selectedDate().toString("dd.MM.yyyy")
        result = capitalize_words(self.result_input.text())
        record_id = self.record_selector.currentData()
        medworker_id = self.medworker_selector.currentData()

        if not date_of_result or not result or not record_id or not medworker_id:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        connection = sqlite3.connect('medical_system.db')
        cursor = connection.cursor()

        if hasattr(self, 'result_id') and self.result_id:
            cursor.execute(
                "UPDATE Analysis_Results SET Date_of_Result=?, Result=?, ID_record=?, ID_medworker=? WHERE ID_result=?",
                (date_of_result, result, record_id, medworker_id, self.result_id))
        else:
            cursor.execute(
                "INSERT INTO Analysis_Results (ID_record, ID_medworker, Date_of_Result, Result) VALUES (?, ?, ?, ?)",
                (record_id, medworker_id, date_of_result, result))

        connection.commit()
        connection.close()
        self.accept()
