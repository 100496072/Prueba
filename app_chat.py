import os
import sqlite3 as sql
import datetime
from app_relacion import AppRelacion
from app_mensajesdesencriptados import AppChatDesencriptados
from base64 import urlsafe_b64encode, urlsafe_b64decode

from db_functions import get_id_by_name
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
        clave, nonce = AppRelacion.reg_relacion()
        cursor.execute("""INSERT INTO chats (user1_id, user2_id, clave, nonce) VALUES (?,?,?,?)""", (user_1, user_2, clave, nonce))
        conn.commit()
        conn.close()


    @classmethod
    def send_message(cls, sender, recipient , message):
        recipient = get_id_by_name(recipient)["id"]
        conn = sql.connect('cripto.sqlite')
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        cursor.execute("""SELECT id, clave, nonce FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user2_id = ? AND user1_id 
        =?)""", (sender, recipient, sender, recipient))
        chat = cursor.fetchone()
        if chat is None:
            cls.create_relation(sender, recipient)
            cursor.execute("""SELECT id, clave, nonce FROM chats WHERE user1_id = ? AND user2_id = ?""", (sender, recipient))
            chat = cursor.fetchone()
        encrypted_data_key = urlsafe_b64decode(chat["clave"])
        nonce_master = urlsafe_b64decode(chat["nonce"])

        AE_Key_stma = c2
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_simetrica = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

        # Cifrado del mensaje
        nonce = os.urandom(12)
        data = message.encode('utf-8')
        chacha = ChaCha20Poly1305(clave_simetrica)
        ct = chacha.encrypt(nonce, data, None)

        ct_mensaje = urlsafe_b64encode(ct).decode('utf-8')
        nonce_mensaje = urlsafe_b64encode(nonce).decode('utf-8')

        current_date_time = datetime.datetime.now().timestamp()
        cursor.execute(
            """INSERT INTO messages (chat_id, sender_id, recipient_id, message, send_time, nonce) VALUES (?,?,?,?,?,?)""",
            (chat["id"], sender, recipient, ct_mensaje, current_date_time, nonce_mensaje))
        cursor.execute("""UPDATE chats SET last_message = ?, last_message_user = ? WHERE id = ?""",
                       (message, sender, chat["id"]))
        conn.commit()
        conn.close()
