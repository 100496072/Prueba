import os
from storage.json_store_chat import JsonStoreChat
from storage.json_store_chatdesencriptados import JsonStoreChatDesencriptados
from storage.json_store_relaciones import JsonStoreRelaciones
from storage.json_store_login import JsonStoreLogin
from app_relacion import AppRelacion
from app_mensajesdesencriptados import AppChatDesencriptados
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from base64 import urlsafe_b64encode, urlsafe_b64decode
from flask import Flask, render_template, request, redirect, url_for, session


# Leer el archivo de texto
with open('pep.txt', 'r') as file:
    lines = file.readlines()

c2 = b''
# Procesar cada línea del archivo
for line in lines:
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())

class AppChat:
    def __init__(self, recipient, sender, message, nonce):
        self._recipient = recipient
        self._sender = sender
        self._message = message
        self._nonce = nonce

    @property
    def recipient(self):
        return self._recipient

    @property
    def sender(self):
        return self._sender

    @property
    def message(self):
        return self._message

    @property
    def nonce(self):
        return self._nonce

    @classmethod
    def send_message(cls, message, recipient, sender):
        rel = JsonStoreRelaciones()
        users = JsonStoreLogin()
        checked_recipient = users.find_item(wanted_item=recipient, key="_username")
        relacionexiste = False

        for relacion in rel.data_list:
            if ((relacion["_username1"] == sender and relacion["_username2"] == checked_recipient["_username"]) or
                    (relacion["_username1"] == checked_recipient["_username"] and relacion["_username2"] == sender)):

                relacionexiste = True

                encrypted_data_key = urlsafe_b64decode(relacion["_clave"])
                nonce_master = urlsafe_b64decode(relacion["_nonce"])
                AE_Key_stma = c2

                chacha_master = ChaCha20Poly1305(AE_Key_stma)
                clave_publica = chacha_master.decrypt(nonce_master, encrypted_data_key, None)
                nonce = os.urandom(12)
                data = message.encode('utf-8')
                chacha = ChaCha20Poly1305(clave_publica)
                ct = chacha.encrypt(nonce, data, None)

                ct_mensaje = urlsafe_b64encode(ct).decode('utf-8')
                nonce_mensaje = urlsafe_b64encode(nonce).decode('utf-8')

                man = JsonStoreChat()
                communication = cls(checked_recipient["_username"], sender, ct_mensaje, nonce_mensaje)
                man.add_item(communication)

                AppChatDesencriptados.messages_descifrados(sender)

        if relacionexiste is False:
            AppRelacion.reg_relacion(sender, recipient)
            cls.send_message(message, recipient, sender)

        messages = JsonStoreChatDesencriptados()
        users = JsonStoreLogin()
        print(messages.data_list)
        return None


