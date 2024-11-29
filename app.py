import smtplib
import random
import json

from cryptography.exceptions import InvalidKey

from app_cartas import send_letter
from app_mensajesdesencriptados import messages_descifrados
from app_user import reg_user, log_user
from app_chat import send_message
from attributes.attribute_pwd import AttributePwd
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from db_functions import get_name_by_id, get_user_by_id
from storage.json_store_chatdesencriptados import JsonStoreChatDesencriptados
import sqlite3 as sql


with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()

c1 = ""
c3 = ""
c4 = ""

for line in lines:
    if line.startswith("c1"):
        c1 = eval(line.split('=')[1].strip())
    if line.startswith("c3"):
        c3 = eval(line.split('=')[1].strip())
    if line.startswith("c4"):
        c4 = eval(line.split('=')[1].strip())




app = Flask(__name__)
app.config['SECRET_KEY'] = c1
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True


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

def create_db():
    conn = sql.connect('cripto.sqlite')
    conn.commit()
    conn.close()

def create_users_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username string UNIQUE, 
    pwd string NOT NULL,
    salt string NOT NULL,
    rol string NOT NULL,
    correo string NOT NULL,
    public_ip string NULL)
    """)
    conn.commit()
    conn.close()


def create_chat_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL, 
        user2_id INTEGER NOT NULL,
        clave string NOT NULL,
        nonce string NOT NULL,
        last_message_user STRING,
        last_message TEXT,
        FOREIGN KEY (user1_id) REFERENCES users(id),
        FOREIGN KEY (user2_id) REFERENCES users(id),
        FOREIGN KEY (last_message_user) REFERENCES users(id), 
        FOREIGN KEY (last_message) REFERENCES messages(id))
        """)
    conn.commit()
    conn.close()


def create_messages_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    message text NOT NULL,
    send_time timestamp  NOT NULL,
    nonce string NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id),
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (recipient_id) REFERENCES users(id))""")
    conn.commit()
    conn.close()

def create_letters_table():
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()
    conn.execute('PRAGMA foreign_keys = ON')
    cursor.execute("""CREATE TABLE IF NOT EXISTS letters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre string NOT NULL,
    correo string NOT NULL,
    ciudad string NOT NULL,
    pais string NOT NULL,
    date timestamp NOT NULL,
    carta text NOT NULL,
    sign string NOT NULL,
    UNIQUE (nombre, date))""")


def get_users():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM users""")
    return cursor.fetchall()

#Pagina de Inicio
@app.route('/')


@app.route('/PapaNoel', methods=['POST'])
def PapaNoel():
    if request.method == 'POST':
        send_letter(letter=request.form["escribe"], sender=request.form["name"], correo=request.form["email"], country=request.form["country"], city=request.form["city"])

    create_db()
    create_users_table()
    create_chat_table()
    create_messages_table()
    create_letters_table()
    return render_template('PapaNoel.html')

#Pagina de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            if request.form['password1'] == request.form['password2']:
                try:
                    AttributePwd(request.form['password1'])
                    # Si la contraseña es válida, procedemos con el registro
                    if reg_user(request.form['username'], request.form['password1'], request.form['correo']):
                        return redirect(url_for('login'))
                    else:
                        return redirect(url_for('register'))
                except ValueError as e:
                    print(e)
                    return redirect(url_for('register'))  # Redirige si la contraseña no es válida
            else:
                return redirect(url_for('register'))  # Redirige si las contraseñas no coinciden
        except KeyError as e:
            return f"Falta el campo: {e}", 400
    return render_template('register.html')

#Pagina de inicio de sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('codigofinal', None)
    if request.method == 'POST':
        try:
            log_user(request.form['username'], request.form['password'])
            return redirect(url_for('codigo'))
        except InvalidKey:
            print("La contraseña no es correcta")
    return render_template('login.html')



#Verificacion Codigo de Seguridad
@app.route('/codigo', methods=['GET', 'POST'])
def codigo():
    if 'codigofinal' not in session:
        session['codigofinal'] = codigocorreo()

    codigofinal = session['codigofinal']

    if request.method == 'POST':
        codigoform = request.form['codigo']

        if codigofinal == int(codigoform):
            man = JsonStoreChatDesencriptados()
            man.vaciar_json()
            return redirect(url_for('chat'))

    return render_template('codigo.html')



#Pagina de Chats
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    messages = None
    users = get_users()

    if request.method == 'POST':
        send_message(message= request.form['message'], recipient= request.form['recipient'], sender= session['user_id'])

    selected_user = request.args.get('user')
    if selected_user:
        messages = messages_descifrados(selected_user, session['user_id'])

    return render_template('chat.html', messages= messages, users = users, username=get_name_by_id(session['user_id'])["username"])



#Envio código de seguridad
def codigocorreo():
    user = get_user_by_id(session["user_id"])
    print(user)
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









if __name__ == '__main__':
    app.run(debug=True)
