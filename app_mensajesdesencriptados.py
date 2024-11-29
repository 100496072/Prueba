from base64 import urlsafe_b64decode
from requests import session
from flask import session
from db_functions.user_functions import get_name_by_id
from db_functions.chat_functions import get_chat_by_id

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import sqlite3 as sql

# Leer el archivo de texto
with open('pep.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

c2 = b''
# Procesar cada línea del archivo
for line in lines:
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())



def get_chat(sender, recipient):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT id, clave, nonce FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user2_id = ? AND user1_id 
            =?)""", (sender, recipient, sender, recipient))
    return cursor.fetchone()


def get_messages(sender, recipient):
    chat = get_chat(sender, recipient)
    if chat is None:
        return "Empty"
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT message, nonce, sender_id FROM messages WHERE chat_id = ?""", (chat["id"],))
    rows = cursor.fetchall()
    message_dict = [dict(row) for row in rows]
    for message in message_dict:
        message["chat_id"] = chat["id"]
        sender_usr = get_name_by_id(message["sender_id"])["username"]
        if sender_usr == get_name_by_id(session["user_id"])["username"]:
            message["sender"] = "Tú"
        else:
            message["sender"] = sender_usr
    return message_dict


def messages_descifrados(sender, recipient):

    message_dict = get_messages(sender, recipient)
    if message_dict == "Empty":
        return message_dict
    #Descifrado de los mensajes del usario con la sesion iniciada
    for mensaje in message_dict:
        mensajecifrado = urlsafe_b64decode(mensaje["message"])
        noncemensaje = urlsafe_b64decode(mensaje["nonce"])
        chat_id = mensaje["chat_id"]
        chat = get_chat_by_id(chat_id)

        encrypted_data_key = urlsafe_b64decode(chat["clave"])
        nonce_master = urlsafe_b64decode(chat["nonce"])
        AE_Key_stma = c2

        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_publica = chacha_master.decrypt(nonce_master, encrypted_data_key, None)


        chacha_data = ChaCha20Poly1305(clave_publica)
        mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)

        mensaje["message"] = mensajefinal.decode('utf-8')

    return message_dict