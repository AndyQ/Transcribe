import sqlite3
import datetime

from .constants import Paths

def get_db_connection():
    conn = sqlite3.connect(f'{Paths.instance}/database.db')
    conn.row_factory = sqlite3.Row
    return conn


def addItem( task ):
    conn = get_db_connection()

    cursor=conn.cursor()

    print( task )

    cursor.execute('INSERT INTO item (title, type, file_name, status) VALUES (?, ?, ?, ?)',
                 (task['title'], task['type'], task['file_name'], 'waiting'))
    rowid = cursor.lastrowid
    conn.commit()

    # Get id from last insert
    cursor.execute('SELECT id FROM item WHERE rowid = ?', (rowid,))
    row = cursor.fetchone()
    conn.close()

    (inserted_id,) = row if row else None
    return inserted_id

def getItems():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item')
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()


    return rows

def getItem( id ):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item WHERE id = ?', (id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)

def deleteItem( id ):
    conn = get_db_connection()
    conn.execute('DELETE FROM item WHERE id = ?', (id,))
    conn.commit()
    conn.close()


def getItemsWithStatus( status ):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item WHERE status = ?', (status,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return rows

def getFirstWaitingItem():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item WHERE status = "waiting" LIMIT 1')
    row = cur.fetchone()
    conn.close()

    # # If no jobs, see if any pending
    # if row == None:
    #     cur.execute('SELECT * FROM item WHERE status = "waiting" LIMIT 1')

    #     return None

    return row

def updateItemStatus( id, status ):
    conn = get_db_connection()
    conn.execute('UPDATE item SET status = ?, status_updated = ? WHERE id = ?',
                 (status, datetime.datetime.now(), id))
    conn.commit()
    conn.close()

def updateTranscriptionFile( id, transcriptionFile ):
    conn = get_db_connection()
    conn.execute('UPDATE item SET transcription_file = ? WHERE id = ?',
                 (transcriptionFile, id))
    conn.commit()
    conn.close()

