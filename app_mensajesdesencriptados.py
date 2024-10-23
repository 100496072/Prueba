from base64 import urlsafe_b64decode
from storage.json_store_chat import JsonStoreChat
from storage.json_store_chatdesencriptados import JsonStoreChatDesencriptados
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

class AppChatDesencriptados:
    def __init__(self, recipient, sender, message):
        self._recipient = recipient
        self._sender = sender
        self._message = message

    @property
    def recipient(self):
        return self._recipient

    @property
    def sender(self):
        return self._sender

    @property
    def message(self):
        return self._message



    @classmethod
    def messages_descifrados(cls, sender):
        mensajestotales = JsonStoreChat()
        rel = JsonStoreRelaciones()

        man = JsonStoreChatDesencriptados()
        man.vaciar_json()

        #Descifrado de los mensajes del usario con la sesion iniciada
        for mensajes in mensajestotales.data_list:
            if mensajes["_recipient"] == sender or mensajes["_sender"] == sender:

                mensajecifrado = urlsafe_b64decode(mensajes["_message"])
                noncemensaje = urlsafe_b64decode(mensajes["_nonce"])

                for relacion in rel.data_list:
                    if ((relacion["_username1"] == sender and relacion["_username2"] == mensajes["_recipient"] )
                            or (relacion["_username1"] == sender and relacion["_username2"] == mensajes["_sender"])
                            or (relacion["_username2"] == sender and relacion["_username1"] == mensajes["_sender"])
                            or (relacion["_username2"] == sender and relacion["_username1"] == mensajes["_recipient"])):


                        encrypted_data_key = urlsafe_b64decode(relacion["_clave"])
                        nonce_master = urlsafe_b64decode(relacion["_nonce"])
                        AE_Key_stma = c2

                        chacha_master = ChaCha20Poly1305(AE_Key_stma)
                        clave_publica = chacha_master.decrypt(nonce_master, encrypted_data_key, None)


                        chacha_data = ChaCha20Poly1305(clave_publica)
                        mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)

                        mensajefinalutf8 = mensajefinal.decode('utf-8')


                        communication = cls(recipient=mensajes["_recipient"], sender=mensajes["_sender"],
                                            message=mensajefinalutf8)
                        man.add_item(communication)
                        break


        return None