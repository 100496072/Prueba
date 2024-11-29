import sqlite3 as sql


def get_chat_by_id(chat_id):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
    return cursor.fetchone()


def update_last_message(message, sender, chat_id):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""UPDATE chats SET last_message = ?, last_message_user = ? WHERE id = ?""",
                   (message, sender, chat_id))
    conn.commit()
    conn.close()
