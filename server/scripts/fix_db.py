import sqlite3

conn = sqlite3.connect('instance/database.db')
conn.row_factory = sqlite3.Row


cur = conn.cursor()
cur.execute('alter table item add column source_url text')
cur.execute('alter table item rename to temp_item' )
cur.execute("""CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    source_url TEXT,
    transcription_file TEXT,
    status TEXT NOT NULL,
    status_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")
cur.execute('insert into item(id, created, title, type, file_name, source_url, transcription_file, status, status_updated) select id, created, title, type, file_name, source_url, transcription_file, status, status_updated from temp_item')
cur.execute('drop table temp_item')

cur.execute('SELECT * FROM item where type = "youtube"')

rows = [dict(row) for row in cur.fetchall()]
for row in rows:
    source_url = f"https://www.youtube.com/watch?v={row['file_name']}"
    cur.execute('UPDATE item SET source_url = ? WHERE id = ?', (source_url, row['id'],))

conn.commit()
conn.close()
