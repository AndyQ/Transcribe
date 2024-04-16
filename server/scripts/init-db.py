import sqlite3

connection = sqlite3.connect('instance/database.db')

try:

    with open('scripts/schema.sql') as f:
        connection.executescript(f.read())
except Exception as e:
    print( "Error in schema.sql: ", e)
connection.commit()
connection.close()
