import sqlite3

conn = sqlite3.connect('instance/database.db')
conn.row_factory = sqlite3.Row


cur = conn.cursor()
cur.execute('alter table item add column error_reason TEXT')

conn.commit()
conn.close()
