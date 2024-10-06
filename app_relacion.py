import base64

from cryptography.hazmat.primitives import serialization

from storage.json_store_login import JsonStoreLogin
from storage.json_store_relaciones import JsonStoreRelaciones
from cryptography.hazmat.primitives.asymmetric import rsa



class AppRelacion:
    def __init__(self, username1 , username2):
        self._username1 = username1
        self._username2 = username2

    @property
    def username1(self):
        return self._username1

    @property
    def username2(self):
        return self._username2

    @classmethod
    def reg_relacion(cls, username1, username2):
        print("c")
        private_key1 = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key1 = private_key1.public_key()

        private_key2 = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key2 = private_key2.public_key()

        private_key_bytes1 = private_key1.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b'my_password')
        )

        # Serializar clave pública
        public_key_bytes1 = public_key1.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        private_key_bytes2 = private_key2.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b'my_password')
        )

        # Serializar clave pública
        public_key_bytes2 = public_key2.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        private_key_str1 = base64.b64encode(private_key_bytes1).decode('utf-8')
        public_key_str1 = base64.b64encode(public_key_bytes1).decode('utf-8')

        private_key_str2 = base64.b64encode(private_key_bytes2).decode('utf-8')
        public_key_str2 = base64.b64encode(public_key_bytes2).decode('utf-8')

        users = JsonStoreLogin()
        for usuario in users.data_list:
            if usuario["_username"] == username1:
                usuario["_claves"].append([username2, public_key_str1, private_key_str1, public_key_str2])

            if usuario["_username"] == username2:
                usuario["_claves"].append([username1, public_key_str2, private_key_str2, public_key_str1])

        rel = JsonStoreRelaciones()
        new_user = cls(username1=username1, username2=username2)
        rel.add_item(new_user)
        users.save_store()

        return None