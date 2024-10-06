
from storage.json_store_chat import JsonStoreChat
from storage.json_store_relaciones import JsonStoreRelaciones
from storage.json_store_login import JsonStoreLogin
from app_relacion import AppRelacion
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64


class AppChat:
    def __init__(self, message, recipient, sender):
        self._message = message
        self._recipient = recipient
        self._sender = sender

    @property
    def message(self):
        return self._message

    @property
    def recipient(self):
        return self._recipient

    @property
    def sender(self):
        return self._sender

    @classmethod
    def send_message(cls, message, recipient, sender):
        rel = JsonStoreRelaciones()
        users = JsonStoreLogin()
        checked_recipient = users.find_item(wanted_item=recipient, key="_username")
        relacionexiste = False

        for relacion in rel.data_list:
            if ((relacion["_username1"] == sender and relacion["_username2"] == checked_recipient["_username"]) or
                    (relacion["_username1"] == checked_recipient["_username"] and relacion["_username2"] == sender)):
                for user in users.data_list:
                    if user["_username"] == sender:
                        claves = user["_claves"]
                        cablepublica = None

                        for clave in claves:
                            if clave[0] == checked_recipient["_username"]:
                                cablepublica = clave[3]

                        public_key_bytes = base64.b64decode(cablepublica)

                        public_key = serialization.load_pem_public_key(
                            public_key_bytes,
                            backend=default_backend()
                        )

                        mensajebytes =  message.encode('utf-8')
                        ciphertext = public_key.encrypt(
                            mensajebytes,
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None
                            )
                        )

                        ciphertextbase64 = base64.b64encode(ciphertext).decode('utf-8')
                        man = JsonStoreChat()
                        communication = cls(ciphertextbase64, checked_recipient["_username"], sender)
                        man.add_item(communication)
                        relacionexiste = True

        if relacionexiste is False:
            AppRelacion.reg_relacion(sender, recipient)
            cls.send_message(message, recipient, sender)
        return None

