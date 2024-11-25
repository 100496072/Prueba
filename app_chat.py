import os
import sqlite3 as sql
import datetime
from app_relacion import AppRelacion
from app_mensajesdesencriptados import AppChatDesencriptados
from base64 import urlsafe_b64encode, urlsafe_b64decode
from storage.json_store_chat import JsonStoreChat
from storage.json_store_login import JsonStoreLogin
from storage.json_store_relaciones import JsonStoreRelaciones
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


# Leer el archivo de texto
with open('pep.txt', 'r', encoding='utf-8') as file:
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
    def create_relation(cls,user_1, user_2):
        conn = sql.connect('cripto.sqlite')
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO chat (user1_id, user2_id) VALUES (?,?)""", (user_1, user_2))
        conn.commit()
        conn.close()
    @classmethod
    def send_message(cls,user1, user2, message, nonce):
        conn = sql.connect('cripto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""SELECT chat_id FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user2_id = ? AND user1_id 
        =?)""", (user1, user2, user1, user2))
        chat_id = cursor.fetchone()
        if chat_id is None:
            cls.create_relation(user1, user2)
            cursor.execute("""SELECT chat_id FROM chats WHERE user1_id = ? AND user2_id = ?""", (user1, user2))
            chat_id = cursor.fetchone()
        current_date_time = datetime.datetime.now().timestamp()
        cursor.execute(
            """INSERT INTO messages (chat_id, sender_id, recipient_id, message, send_time, nonce) VALUES (?,?,?,?,?,?)""",
            (chat_id[0], user1, user2, message, current_date_time, nonce))
        cursor.execute("""UPDATE chats SET last_message = ?, last_message_user = ? WHERE chat_id = ?""",
                       (message, user1, chat_id[0]))
        conn.commit()
        conn.close()

    @classmethod
    def send_message(cls, message, recipient, sender):
        rel = JsonStoreRelaciones()
        users = JsonStoreLogin()
        checked_recipient = users.find_item(wanted_item=recipient, key="_username")
        relacionexiste = False


        #Verificacion de si ha habido un contacto previo entre usuarios
        for relacion in rel.data_list:
            if ((relacion["_username1"] == sender and relacion["_username2"] == checked_recipient["_username"]) or
                    (relacion["_username1"] == checked_recipient["_username"] and relacion["_username2"] == sender)):

                relacionexiste = True

                encrypted_data_key = urlsafe_b64decode(relacion["_clave"])
                nonce_master = urlsafe_b64decode(relacion["_nonce"])

                AE_Key_stma = c2
                chacha_master = ChaCha20Poly1305(AE_Key_stma)
                clave_simetrica = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

                #Cifrado del mensaje
                nonce = os.urandom(12)
                data = message.encode('utf-8')
                chacha = ChaCha20Poly1305(clave_simetrica)
                ct = chacha.encrypt(nonce, data, None)

                ct_mensaje = urlsafe_b64encode(ct).decode('utf-8')
                nonce_mensaje = urlsafe_b64encode(nonce).decode('utf-8')

                #Guardado del mensaje cifrado
                man = JsonStoreChat()
                communication = cls(checked_recipient["_username"], sender, ct_mensaje, nonce_mensaje)
                man.add_item(communication)

                AppChatDesencriptados.messages_descifrados(sender)


        #Si nunca ha habido un contacto previo lo creamos
        if relacionexiste is False:
            if sender != recipient:
                AppRelacion.reg_relacion(sender, recipient)
                cls.send_message(message, recipient, sender)

        return None


