import datetime
from inspect import signature
import sqlite3 as sql
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key



"""def insert_letter(letter, sender, correo, city, country, firma):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute(INSERT INTO letters (nombre, correo, ciudad, pais, carta, sign) VALUES (?,?,?,?,?,?), (sender, correo, city, country,letter, firma))
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
    insert_letter(letter, sender, correo, city, country, letter_signature)"""

