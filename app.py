from flask import Flask, render_template, request, redirect, url_for, session
import json
from flask_wtf import FlaskForm
from pyexpat.errors import messages
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
#import socket
import requests
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from app_user import AppUser
from app_chat import AppChat
from storage.json_store_login import JsonStoreLogin
from storage.json_store_chat import JsonStoreChat

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
        AppUser.reg_user(request.form['username'], request.form['password'], request.form['correo'])
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global codigofinal
    if request.method == 'POST':
        if AppUser.log_user(request.form['username'], request.form['password']):
            return redirect(url_for('codigo'))
        else:
            return redirect(url_for('chat'))

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
    print(session)
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        AppChat.send_message(message= request.form['message'], recipient= request.form['recipient'], sender= session['username'])
    messages = JsonStoreChat()
    users = JsonStoreLogin()
    return render_template('chat.html', messages= messages.data_list, users= users.data_list, username=session['username'])

@app.route('/PapaNoel', methods=['POST'])
def PapaNoel():

    if request.method == 'POST':
        carta = request.form['escribe']
        
    return render_template('PapaNoel.html')

if __name__ == '__main__':
    app.run(debug=True)
