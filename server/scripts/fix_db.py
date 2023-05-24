import sqlite3

conn = sqlite3.connect('instance/database.db')
conn.row_factory = sqlite3.Row


cur = conn.cursor()

cur.execute('SELECT * FROM item where type = "youtube"')

rows = [dict(row) for row in cur.fetchall()]
for row in rows:
    source_url = f"https://www.youtube.com/watch?v={row['source_url']}"
    cur.execute('UPDATE item SET source_url = ? WHERE id = ?', (source_url, row['id'],))

conn.commit()
conn.close()
