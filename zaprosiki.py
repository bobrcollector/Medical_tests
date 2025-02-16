import sqlite3

connection = sqlite3.connect('medical_system.db')

cursor = connection.cursor()

"""Очищает все данные из базы данных 


cursor.execute('''DELETE FROM Analysis_Results''')

cursor.execute('''DELETE FROM Analyses''')

cursor.execute('''DELETE FROM Analysis_Categories''')

cursor.execute('''DELETE FROM Medworkers''')

cursor.execute('''DELETE FROM Patient_Records''')

cursor.execute('''DELETE FROM Patients''') """

connection.commit()
connection.close()