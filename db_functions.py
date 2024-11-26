import sqlite3 as sql


def get_name_by_id(user_id):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()

def get_chat_by_id(chat_id):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
    return cursor.fetchone()

def get_id_by_name(username):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def get_user_by_id(user_id):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()