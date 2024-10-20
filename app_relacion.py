
from storage.json_store_relaciones import JsonStoreRelaciones
import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode


class AppRelacion:
    def __init__(self, username1 , username2, clave, nonce):
        self._username1 = username1
        self._username2 = username2
        self._clave = clave
        self._nonce = nonce

    @property
    def username1(self):
        return self._username1

    @property
    def username2(self):
        return self._username2

    @property
    def clave(self):
        return self._clave

    @property
    def nonce(self):
        return self._nonce

    @classmethod
    def reg_relacion(cls, username1, username2):

        key = ChaCha20Poly1305.generate_key()

        AE_Key_stma = b'0123456789ABCDEF0123456789ABCDEF'
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        nonce_master = os.urandom(12)

        encrypted_data_key = chacha_master.encrypt(nonce_master, key, None)

        public_key = urlsafe_b64encode(encrypted_data_key).decode('utf-8')
        nonce_maestro = urlsafe_b64encode(nonce_master).decode('utf-8')


        rel = JsonStoreRelaciones()
        new_user = cls(username1=username1, username2=username2, clave=public_key, nonce=nonce_maestro)
        rel.add_item(new_user)

        return None