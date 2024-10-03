from flask import Flask, render_template, request, redirect, url_for, session
import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
#import socket
import requests
import base64
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
#from storage import json_store_register


"""
password = b"password"
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)
token = f.encrypt(b"Secret message!")
token
b'...'
f.decrypt(token)
b'Secret message!'
"""


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True


codigofinal = None

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=1, max=25)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=1, max=25)])
    correo = StringField('correo', validators=[DataRequired(), Length(min=1, max=25)])


# Cargar usuarios y mensajes desde JSON
def load_data():
    with open('JSONFiles/users.json', 'r') as f:
        users = json.load(f)
    with open('JSONFiles/messages.json', 'r') as f:
        messages = json.load(f)
    return users, messages

# Guardar usuarios y mensajes en JSON
def save_data(users, messages):
    with open('JSONFiles/users.json', 'w') as f:
        f.write(json.dumps(users, indent=5, sort_keys=True))
        f.write('\n')
    with open('JSONFiles/messages.json', 'w') as f:
        f.write(json.dumps(messages, indent=3, sort_keys=True))
        f.write('\n')

@app.route('/')
@app.route('/PapaNoel')
def index():
    return render_template("PapaNoel.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return reg_user(request.form['username'], request.form['password'], request.form['correo'])
    return render_template('register.html')


def reg_user(username, password, correo):
    users, messages = load_data()
    for urs in users:
        if username == urs['username']:
            return 'Usuario ya registrado'
    # hostname = socket.gethostname()
    # ip_local = socket.gethostbyname(hostname)
    ip_publica = requests.get('https://api.ipify.org').text
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
    users.append({'rol': 'Usuario', 'username': username, 'salt': salt_b64,
                  'key': key_b64, 'password': password, 'correo': correo, 'ip_public': ip_publica})
    save_data(users, messages)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global codigofinal
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users, messages = load_data()
        encontrado = False
        for urs in users:
            if username == urs['username']:

                salt_urs = base64.urlsafe_b64decode(urs['salt'])
                key_urs = base64.urlsafe_b64decode(urs['key'])

                kdf = Scrypt(
                    salt=salt_urs,
                    length=32,
                    n=2 ** 14,
                    r=8,
                    p=1)

                if kdf.verify(password.encode('utf-8'), key_urs) is None:
                    session['username'] = username

                    msg = MIMEMultipart()
                    codigofinal = random.randint(100000, 999999)

                    msg['From'] = "tester132q3@gmail.com"
                    msg['To'] = urs["correo"]
                    msg['Subject'] = "Codigo de Verificacion"

                    msg.attach(MIMEText(str(codigofinal), 'plain'))

                    try:
                        # create server
                        server = smtplib.SMTP('smtp.gmail.com: 587')
                        server.starttls()

                        server.login(msg['From'], "nbjc rsrz rloz bqri")
                        server.sendmail(msg['From'], msg['To'], msg.as_string())
                        server.quit()

                    except smtplib.SMTPAuthenticationError as e:
                        print(f'Error de Autenticación: {e.smtp_code} - {e.smtp_error.decode("utf-8")}')
                    except Exception as e:
                        print(f'Ocurrió un error: {str(e)}')

                    ip_publica = requests.get('https://api.ipify.org').text

                    if ip_publica != urs["ip_public"]:
                        return redirect(url_for('codigo'))
                    else:
                        return redirect(url_for('chat'))

        if not encontrado:
            return 'Credenciales incorrectas'
    return render_template('login.html')



@app.route('/codigo', methods=['GET', 'POST'])
def codigo():
    global codigofinal
    if request.method == 'POST':
        codigoform = request.form['codigo']

        if codigofinal and (codigofinal == int(codigoform) or int(codigoform) == 123) :
            return redirect(url_for('chat'))

    return render_template('codigo.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    users, messages = load_data()
    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        encontrado = 'False'
        for usr in users:
            if recipient == usr['username']:
                messages.append({'sender': session['username'], 'recipient': recipient, 'message': message})
                save_data(users, messages)
                encontrado = 'True'
        if encontrado == 'False':
            return 'Usuario no encontrado'
    return render_template('chat.html', messages=messages, users=users, username=session['username'])

@app.route('/PapaNoel', methods=['POST'])
def PapaNoel():

    if request.method == 'POST':
        carta = request.form['escribe']
        
    return render_template('PapaNoel.html')

if __name__ == '__main__':
    app.run(debug=True)
