import sqlite3 as sql


def insert_message(chat_id, sender, recipient, ct_mensaje, current_date_time, nonce_mensaje):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO messages (chat_id, sender_id, recipient_id, message, send_time, nonce) VALUES (?,?,?,?,?,?)""",
        (chat_id, sender, recipient, ct_mensaje, current_date_time, nonce_mensaje))
    conn.commit()
    conn.close()
