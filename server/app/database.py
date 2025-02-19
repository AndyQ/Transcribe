import sqlite3
import datetime

from .constants import Paths


def get_db_connection():
    conn = sqlite3.connect(f"{Paths.instance}/database.db")
    conn.row_factory = sqlite3.Row
    return conn


def addItem(task):
    conn = get_db_connection()

    cursor = conn.cursor()

    print(task)

    source_url = task.get("source_url", task.get("url"))
    status = task.get("status", "waiting")
    cursor.execute(
        "INSERT INTO item (title, type, file_name, source_url, status) VALUES (?, ?, ?, ?, ?)",
        (task["title"], task["type"], task["file_name"], source_url, status),
    )
    rowid = cursor.lastrowid
    conn.commit()

    # Get id from last insert
    cursor.execute("SELECT id FROM item WHERE rowid = ?", (rowid,))
    row = cursor.fetchone()
    conn.close()

    if row:
        (inserted_id,) = row
        return inserted_id
    else:
        return None


def getItems():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM item order by status_updated desc")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return rows


def getItem(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM item WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


def deleteItem(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM item WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def getItemsWithStatus(status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM item WHERE status = ?", (status,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return rows


def getFirstWaitingItem():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM item WHERE status = "waiting" LIMIT 1')
    row = cur.fetchone()
    conn.close()

    return row


def updateItemType(id, type):
    conn = get_db_connection()
    conn.execute("UPDATE item SET type = ? WHERE id = ?", (type, id))
    conn.commit()
    conn.close()


def updateItemFilename(id, filename):
    conn = get_db_connection()
    conn.execute("UPDATE item SET file_name = ? WHERE id = ?", (filename, id))
    conn.commit()
    conn.close()


def updateItemStatus(id, status, error_message=None):
    conn = get_db_connection()
    conn.execute(
        "UPDATE item SET status = ?, status_updated = ?, error_reason = ? WHERE id = ?",
        (status, datetime.datetime.now(), error_message, id),
    )
    conn.commit()
    conn.close()


def updateTranscriptionFile(id, transcriptionFile):
    conn = get_db_connection()
    conn.execute(
        "UPDATE item SET transcription_file = ? WHERE id = ?", (transcriptionFile, id)
    )
    conn.commit()
    conn.close()
