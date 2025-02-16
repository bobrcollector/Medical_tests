import sqlite3

connection = sqlite3.connect('medical_system.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Patients (
    ID_patient INTEGER PRIMARY KEY AUTOINCREMENT,
    Last_Name TEXT,
    First_Name TEXT,
    Middle_Name TEXT,
    Date_of_Birth TEXT,
    Gender TEXT,
    Contact_Phone TEXT
)
''') # реализация Patients
cursor.execute('''
CREATE TABLE IF NOT EXISTS Patient_Records (
    ID_record INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_patient INTEGER,
    Date_of_Appointment TEXT,
    Time_of_Appointment TEXT,
    ID_analysis INTEGER,
    FOREIGN KEY (ID_patient) REFERENCES Patients(ID_patient),
    FOREIGN KEY (ID_analysis) REFERENCES Analyses(ID_analysis)
)
''') # реализация Patient_Records
cursor.execute('''
CREATE TABLE IF NOT EXISTS Medworkers (
    ID_medworker INTEGER PRIMARY KEY AUTOINCREMENT,
    Last_Name TEXT,
    First_Name TEXT,
    Middle_Name TEXT,
    Login TEXT,
    Passwd TEXT
)
''') # реализация Medworkers
cursor.execute('''
CREATE TABLE IF NOT EXISTS Analyses (
    ID_analysis INTEGER PRIMARY KEY AUTOINCREMENT,
    Analysis_Name TEXT,
    ID_analysis_category INTEGER,
    FOREIGN KEY (ID_analysis_category) REFERENCES Analysis_Categories(ID_analysis_category)
)
''') # реализация Analyses
cursor.execute('''
CREATE TABLE IF NOT EXISTS Analysis_Categories (
    ID_analysis_category INTEGER PRIMARY KEY AUTOINCREMENT,
    Category_Name TEXT
)
''') # реализация Analysis_Categories
cursor.execute('''
CREATE TABLE IF NOT EXISTS Analysis_Results (
    ID_result INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_record INTEGER,
    ID_medworker INTEGER,
    Date_of_Result TEXT,
    Result TEXT,
    FOREIGN KEY (ID_record) REFERENCES Patient_Records(ID_record),
    FOREIGN KEY (ID_medworker) REFERENCES Medworkers(ID_medworker)
)
''') # реализация Analysis_Results

connection.commit()
connection.close()

