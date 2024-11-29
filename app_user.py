import base64
import os
import requests
from flask import session
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import sqlite3 as sql

#Función para el registro de nuevos usuarios

def reg_user(username, password, correo):

    if look_info(username) is not None:
        return False


    salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 14,
        r=8,
        p=1,
    )

    key = kdf.derive(password.encode('utf-8'))
    salt_b64 = base64.urlsafe_b64encode(salt).decode('utf-8')
    key_b64 = base64.urlsafe_b64encode(key).decode('utf-8')

    insert_user(nombre=username, salt= salt_b64, pwd= key_b64, correo= correo)

    return True



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


def look_info(user):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users WHERE username = ?""", (user,))
    return cursor.fetchone()

def set_ip( ip, user):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""UPDATE users SET public_ip = ? WHERE id = ?""", (ip, user))
    conn.commit()
    conn.close()
#Función para el inicio de usuarios

def log_user(username, password):

    info  = look_info( username)
    if info is None:
        print("No existe el usuario")
    else:
        l_salt = info["salt"]
        kdf = Scrypt(
            salt= base64.urlsafe_b64decode(l_salt),
            length=32,
            n=2 ** 14,
            r=8,
            p=1)

        l_pwd = info["pwd"]
        #Verificacion de contraseña correcta
        if kdf.verify(password.encode('utf-8'), base64.urlsafe_b64decode(l_pwd)) is None:
            session["user_id"] = info["id"]
            print(session["user_id"])
            #Verificacion ip publica igual a la ip publica del registro original
            ip_publica = requests.get('https://api.ipify.org').text
            l_ip_publica = info["public_ip"]
            if ip_publica != l_ip_publica:
                set_ip(ip_publica, info["id"])
                return True
            else:
                return False
