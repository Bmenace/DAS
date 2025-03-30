# Installed mysql on computer 
# pip install mysql
# pip install mysql-connector-python


import mysql.connector

dataBase = mysql.connector.connect(
    host = 'localhost', 
    user = 'root',
    passwd = 'password123'

    )

# Prepare a cursor object
cursorObject = dataBase.cursor()

# Create a database
cursorObject.execute('CREATE DATABASE DAS_records')

print('All Done')

