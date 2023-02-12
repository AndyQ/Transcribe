import sqlite3

connection = sqlite3.connect('instance/database.db')


with open('scripts/schema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
