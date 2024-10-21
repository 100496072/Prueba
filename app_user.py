import base64
import os
import random
import smtplib
import requests
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import session
from storage.json_store_register import JsonStoreRegister
from storage.json_store_login import JsonStoreLogin


class AppUser:
    def __init__(self,rol , username, salt, key, password, correo, public_ip):
        self._rol = rol
        self._username = username
        self._salt = salt
        self._key = key
        self._password = password
        self._correo = correo
        self._public_ip = public_ip


    @property
    def username(self):
        return self._username

    @property
    def salt(self):
        return self._salt

    @property
    def key(self):
        return self._key

    @property
    def password(self):
        return self._password

    @property
    def public_ip(self):
        return self._public_ip


    @classmethod
    def reg_user(cls,username, password, correo):
        man = JsonStoreRegister()
        man.find_item(username, "_username")
        # hostname = socket.gethostname()
        # ip_local = socket.gethostbyname(hostname)
        ip_publica = requests.get('https://api.ipify.org').text
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
        new_user = cls(rol='Usuario', username= username, salt= salt_b64,
                      key= key_b64, password= password, correo= correo, public_ip= ip_publica)
        man.add_item(new_user)
        return None

    @classmethod
    def log_user(cls, username, password):
        man = JsonStoreLogin()
        user = man.find_item(username, "_username")
        salt_urs = base64.urlsafe_b64decode(user['_salt'])
        key_urs = base64.urlsafe_b64decode(user['_key'])

        kdf = Scrypt(
            salt=salt_urs,
            length=32,
            n=2 ** 14,
            r=8,
            p=1)

        if kdf.verify(password.encode('utf-8'), key_urs) is None:
            session['username'] = username

            ip_publica = requests.get('https://api.ipify.org').text

            if ip_publica != user["_public_ip"]:
                return True
            else:
                return False
