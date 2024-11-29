import os
import datetime
from app_relacion import create_relation, search_relation
from base64 import urlsafe_b64encode, urlsafe_b64decode

from db_functions.user_functions import get_id_by_name
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from db_functions.chat_functions import update_last_message
from db_functions.message_functions import insert_message

# Leer el archivo de texto
with open('pep.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

c2 = b''
# Procesar cada línea del archivo
for line in lines:
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())


def send_message( sender, recipient , message):
    recipient = get_id_by_name(recipient)["id"]
    chat = search_relation(sender, recipient)
    if chat is None:
        create_relation(sender, recipient)
        chat = search_relation(sender, recipient)
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

    insert_message(chat["id"], sender, recipient, ct_mensaje, current_date_time, nonce_mensaje)
    update_last_message(message, sender, chat["id"])

