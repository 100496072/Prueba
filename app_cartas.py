import datetime
from inspect import signature
import sqlite3 as sql

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()
c5 = ""
for line in lines:
    if line.startswith("c5"):
        c5 = eval(line.split('=')[1].strip())

with open("private_key.pem", "rb") as key_file:
    rsa_private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=c5,
    )
with open("01.pem", "rb") as file:
    AC1cert = x509.load_der_x509_certificate(
        file.read()
    )

def insert_letter(letter, sender, correo, city, country, firma):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO letters (nombre, correo, ciudad, pais, carta, sign) VALUES (?,?,?,?,?,?)""", (sender, correo, city, country,letter, firma))
    conn.commit()
    conn.close()

def send_letter(letter, sender, correo, city, country):
    letter_signature = rsa_private_key.sign(
        letter.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    insert_letter(letter, sender, correo, city, country, letter_signature)

