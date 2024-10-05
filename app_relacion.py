from storage.json_store_relaciones import JsonStoreRelaciones
from cryptography.hazmat.primitives.asymmetric import rsa



class AppRelacion:
    def __init__(self, username1 , username2, public_key):
        self._username1 = username1
        self._username2 = username2
        self._public_key = None

    @property
    def username1(self):
        return self._username1

    @property
    def username2(self):
        return self._username2

    @property
    def public_key(self):
        return self._public_key

    @classmethod
    def reg_relacion(cls, username1, username2):

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        rel = JsonStoreRelaciones()
        new_user = cls(username1=username1, username2=username2, public_key = public_key)
        rel.add_item(new_user)
        return None