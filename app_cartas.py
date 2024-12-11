import datetime

from email.mime.multipart import MIMEMultipart
import smtplib
import random
from email.mime.text import MIMEText


from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from db_functions.letter_functions import insert_letter, get_letter


with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()
private_key_pwd = ""
c3 = ""
c4 = ""

for line in lines:
    if line.startswith("c5"):
        private_key_pwd = eval(line.split('=')[1].strip())
    if line.startswith("c3"):
        c3 = eval(line.split('=')[1].strip())
    if line.startswith("c4"):
        c4 = eval(line.split('=')[1].strip())

with open("Certs&keys/private_key.pem", "rb") as key_file:
    rsa_private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=private_key_pwd,
    )
with open("Certs&keys/01.pem", "rb") as file:
    Acert = x509.load_pem_x509_certificate(
        file.read()
    )
with open("Certs&keys/ac1cert.pem", "rb") as file:
    AC1cert = x509.load_pem_x509_certificate(
        file.read()
    )

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
            AC1cert.signature,  # Firma del certificado
            AC1cert.tbs_certificate_bytes,  # Contenido del certificado que fue firmado
            padding.PKCS1v15(),  # Tipo de padding (normalmente PKCS1v15 para X.509)
            AC1cert.signature_hash_algorithm,  # Algoritmo hash usado (extraído del certificado)
        )
        print("El certificado de la CA es válido y fue firmado por la CA.")
    except Exception as e:
        print(f"El certificado no es válido: {e}")
        return None

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
        return None

    try:
        Acert.public_key().verify(
            letter["sign"],  # Firma obtenida
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
        return None

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def cartascorreo(letter, sender, correo, country, city):
    msg = MIMEMultipart()
    msg['From'] = c4  # Asumiendo que 'c4' es tu correo
    msg['To'] = correo
    msg['Subject'] = "Hemos recibido tu carta"

    # Crea el cuerpo del mensaje utilizando una plantilla
    html_template = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; color: #333; line-height: 1.6; margin: 0; padding: 20px;">
            <div class="container" style="background-color: #ffffff; border-radius: 10px; padding: 20px; max-width: 600px; margin: auto; border: 1px solid #ddd;">
                <h1 style="color: #d32f2f; text-align: center;">🎅 ¡Gracias por tu carta, {sender}!</h1>
                <p>Querido/a {sender},</p>
                <p>
                    Hemos recibido tu carta desde <strong>{city}, {country}</strong>. Nos emociona mucho saber de ti y que nos hayas escrito esto:
                </p>
                <p class="message" style="font-style: italic; color: #555;">"{letter}"</p>
                <p>
                    Muchas gracias por compartir tus deseos. Estamos trabajando arduamente aquí en el Polo Norte para cumplirlos. 
                    Recuerda portarte bien, ¡Santa está observándote! 🎄
                </p>
                <p>Con cariño,</p>
                <p><strong>Santa Claus 🎅</strong></p>
            </div>
        </body>
    </html>
    """

    # Adjuntar la plantilla como contenido HTML
    msg.attach(MIMEText(html_template, 'html'))

    try:
        # Crear servidor
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()

        server.login(msg['From'], c3)  # 'c3' es la contraseña de tu cuenta de correo
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    except smtplib.SMTPAuthenticationError as e:
        print(f'Error de Autenticación: {e.smtp_code} - {e.smtp_error.decode("utf-8")}')
    except Exception as e:
        print(f'Ocurrió un error: {str(e)}')

    return

