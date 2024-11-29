import base64
import os
import requests
from flask import session
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from db_functions.user_functions import look_info, insert_user, set_ip

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


def log_user(username, password):

    info  = look_info(username)
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
            print("hola")
            session["user_id"] = info["id"]
            #Verificacion ip publica igual a la ip publica del registro original
            ip_publica = requests.get('https://api.ipify.org').text
            l_ip_publica = info["public_ip"]
            if ip_publica != l_ip_publica:
                set_ip(ip_publica, info["id"])
                return True
            else:
                return False

