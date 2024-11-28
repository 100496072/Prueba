import datetime
from inspect import signature
import sqlite3 as sql

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()
private_key_pwd = ""
for line in lines:
    if line.startswith("c5"):
        private_key_pwd = eval(line.split('=')[1].strip())

with open("private_key.pem", "rb") as key_file:
    rsa_private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=private_key_pwd,
    )
with open("01.pem", "rb") as file:
    Acert = x509.load_pem_x509_certificate(
        file.read()
    )
with open("ac1cert.pem", "rb") as file:
    AC1cert = x509.load_pem_x509_certificate(
        file.read()
    )

def insert_letter(letter, sender, correo, city, country, firma, letter_time):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO letters (nombre, correo, ciudad, pais, carta, sign, date) VALUES (?,?,?,?,?,?,?)""", (sender, correo, city, country,letter, firma, letter_time))
    conn.commit()
    conn.close()

def get_letter(sender, letter_time):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM letters WHERE (nombre = ? AND date = ?)""", (sender, letter_time))
    return cursor.fetchone()

def send_letter(letter, sender, correo, city, country):
    letter_signature = rsa_private_key.sign(
        letter.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    letter_time = datetime.datetime.now().timestamp()
    insert_letter(letter, sender, correo, city, country, letter_signature, letter_time)
    check_letter(sender, letter_time)

def check_letter(sender, letter_time):
    letter = get_letter(sender, letter_time)
    clave_publica_ca = AC1cert.public_key()
    try:
        clave_publica_ca.verify(
            Acert.signature,  # Firma del certificado
            Acert.tbs_certificate_bytes,  # Contenido del certificado que fue firmado
            padding.PKCS1v15(),  # Tipo de padding (normalmente PKCS1v15 para X.509)
            Acert.signature_hash_algorithm,  # Algoritmo hash usado (extraído del certificado)
        )
        print("El certificado es válido y fue firmado por la CA.")
    except Exception as e:
        print(f"El certificado no es válido: {e}")


    try:
        rsa_private_key.public_key().verify(
            letter["firma"],  # Firma obtenida
            letter["carta"].encode('utf-8'),  # Contenido firmado
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("La firma es válida y coincide con el certificado.")
    except Exception as e:
        print(f"La firma no es válida: {e}")
