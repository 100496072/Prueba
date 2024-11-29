import os
from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# Leer el archivo de texto
with open('pep.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

c2 = b''
# Procesar cada línea del archivo
for line in lines:
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())

    #Creacion de la realacion entre dos personas
def reg_relacion():
    #Creacion clave simetrica
    key = ChaCha20Poly1305.generate_key()

    AE_Key_stma = c2
    chacha_master = ChaCha20Poly1305(AE_Key_stma)
    nonce_master = os.urandom(12)

    #Cifrado clave simetrica
    encrypted_data_key = chacha_master.encrypt(nonce_master, key, None)
    clave_simetrica = urlsafe_b64encode(encrypted_data_key).decode('utf-8')
    nonce_maestro = urlsafe_b64encode(nonce_master).decode('utf-8')

    return clave_simetrica, nonce_maestro