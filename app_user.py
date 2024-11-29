import base64
import os
from email.mime.multipart import MIMEMultipart
import smtplib
import random
from email.mime.text import MIMEText

import requests
from cryptography.exceptions import InvalidKey
from flask import session
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from db_functions.user_functions import look_info, insert_user, set_ip, get_user_by_id

with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()
c3 = ""
c4 = ""

for line in lines:

    if line.startswith("c3"):
        c3 = eval(line.split('=')[1].strip())
    if line.startswith("c4"):
        c4 = eval(line.split('=')[1].strip())
#Función para el registro de nuevos usuarios

def reg_user(username, password, correo):

    if look_info(username) is not None:
        return False
    salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 14,
        r=8,
        p=1,
    )

    key = kdf.derive(password.encode('utf-8'))
    salt_b64 = base64.urlsafe_b64encode(salt).decode('utf-8')
    key_b64 = base64.urlsafe_b64encode(key).decode('utf-8')

    insert_user(nombre=username, salt= salt_b64, pwd= key_b64, correo= correo)

    return True


def log_user(username, password):

    info  = look_info(username)
    if info is None:
        print("No existe el usuario")
    else:
        l_salt = info["salt"]
        kdf = Scrypt(
            salt= base64.urlsafe_b64decode(l_salt),
            length=32,
            n=2 ** 14,
            r=8,
            p=1)

        l_pwd = info["pwd"]
        #Verificacion de contraseña correcta
        try:
            kdf.verify(password.encode('utf-8'), base64.urlsafe_b64decode(l_pwd))
            print("hola")
            session["user_id"] = info["id"]
            #Verificacion ip publica igual a la ip publica del registro original
            ip_publica = requests.get('https://api.ipify.org').text
            l_ip_publica = info["public_ip"]
            if ip_publica != l_ip_publica:
                set_ip(ip_publica, info["id"])
                session["codigofinal"] = codigocorreo()
                print(session["codigofinal"])
                return False
            else:
                return True
        except InvalidKey:
            print("La contraseña no es correcta")
            return False


def codigocorreo():
    user = get_user_by_id(session["user_id"])
    msg = MIMEMultipart()
    codigofinal = random.randint(100000, 999999)

    msg['From'] = c4
    msg['To'] = user["correo"]
    msg['Subject'] = "Codigo de Verificacion"

    msg.attach(MIMEText(str(codigofinal), 'plain'))

    try:
        # create server
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()

        server.login(msg['From'], c3)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    except smtplib.SMTPAuthenticationError as e:
        print(f'Error de Autenticación: {e.smtp_code} - {e.smtp_error.decode("utf-8")}')
    except Exception as e:
        print(f'Ocurrió un error: {str(e)}')

    return codigofinal