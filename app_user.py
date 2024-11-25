import base64
import os
import requests
from flask import session
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import sqlite3 as sql

class AppUser:
    def __init__(self,rol , username, salt, key, correo, public_ip):
        self._rol = rol
        """self._username, self._message = AttributeUser(username).value"""
        self._username = username
        self._salt = salt
        self._key = key
        self._correo = correo
        self._public_ip = public_ip



    @property
    def rol(self):
        return self._rol

    @property
    def username(self):
        return self._username


    """
    @property
    def message(self):
        return self._message
    """


    @property
    def salt(self):
        return self._salt

    @property
    def key(self):
        return self._key

    @property
    def public_ip(self):
        return self._public_ip


    #Función para el registro de nuevos usuarios
    @classmethod
    def reg_user(cls, username, password, correo):

        if cls.look_info(username) is not None:
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

        cls.insert_user(nombre=username, salt= salt_b64, pwd= key_b64, correo= correo)

        return True


    @classmethod
    def insert_user(cls, nombre, pwd, salt, correo, rol="Usuario"):
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

    @classmethod
    def look_info(cls, user):
        conn = sql.connect('cripto.sqlite')
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM users WHERE username = ?""", (user,))
        return cursor.fetchone()
    @classmethod
    def set_ip(cls, ip, user):
        conn = sql.connect('cripto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""UPDATE users SET public_ip = ? WHERE id = ?""", (ip, user))
        conn.commit()
        conn.close()
    #Función para el inicio de usuarios
    @classmethod
    def log_user(cls, username, password):

        info  = cls.look_info( username)
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
                session['username'] = username

                #Verificacion ip publica igual a la ip publica del registro original
                ip_publica = requests.get('https://api.ipify.org').text
                l_ip_publica = info["public_ip"]
                if ip_publica != l_ip_publica:
                    cls.set_ip(ip_publica, info["id"])
                    return True
                else:
                    return False
