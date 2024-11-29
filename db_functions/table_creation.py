import sqlite3 as sql


def create_db():
    conn = sql.connect('cripto.sqlite')
    conn.commit()
    conn.close()

def initialize_db():
    create_db()
    create_users_table()
    create_chat_table()
    create_messages_table()
    create_letters_table()

def create_users_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username string UNIQUE, 
    pwd string NOT NULL,
    salt string NOT NULL,
    rol string NOT NULL,
    correo string NOT NULL,
    public_ip string NULL)
    """)
    conn.commit()
    conn.close()


def create_chat_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL, 
        user2_id INTEGER NOT NULL,
        clave string NOT NULL,
        nonce string NOT NULL,
        last_message_user STRING,
        last_message TEXT,
        FOREIGN KEY (user1_id) REFERENCES users(id),
        FOREIGN KEY (user2_id) REFERENCES users(id),
        FOREIGN KEY (last_message_user) REFERENCES users(id), 
        FOREIGN KEY (last_message) REFERENCES messages(id))
        """)
    conn.commit()
    conn.close()


def create_messages_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    message text NOT NULL,
    send_time timestamp  NOT NULL,
    nonce string NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id),
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (recipient_id) REFERENCES users(id))""")
    conn.commit()
    conn.close()


def create_letters_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS letters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre string NOT NULL,
    correo string NOT NULL,
    ciudad string NOT NULL,
    pais string NOT NULL,
    date timestamp NOT NULL,
    carta text NOT NULL,
    sign string NOT NULL,
    UNIQUE (nombre, date))""")
