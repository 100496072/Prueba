import sqlite3 as sql


def get_name_by_id(user_id):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
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


def get_users():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users""")
    return cursor.fetchall()

def look_info(user):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users WHERE username = ?""", (user,))
    return cursor.fetchone()

def look_info_ban(user):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM ban WHERE correo = ?""", (user,))
    return cursor.fetchone()


def insert_user(nombre, pwd, salt, correo, rol="Usuario"):
    conn = sql.connect('cripto.sqlite')  # Conectar a la base de datos
    cursor = conn.cursor()  # Crear un cursor
    try:
        # Usar placeholders para insertar los valores
        cursor.execute("INSERT INTO users (username, pwd, salt, correo, rol) VALUES (?,?,?,?,?)", (nombre, pwd, salt, correo, rol))
        conn.commit()  # Guardar los cambios
        print(f"Usuario '{nombre}' insertado correctamente.")
    except sql.IntegrityError as e:
        print("Error al insertar:", e)  # Manejar errores de integridad
    finally:
        conn.close()  # Cerrar la conexión


def set_ip(ip, user):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""UPDATE users SET public_ip = ? WHERE id = ?""", (ip, user))
    conn.commit()
    conn.close()
