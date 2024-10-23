import smtplib
import random
import json
from app_user import AppUser
from app_chat import AppChat
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from storage.json_store_chatdesencriptados import JsonStoreChatDesencriptados
from storage.json_store_login import JsonStoreLogin


with open('pep.txt', 'r') as file:
    lines = file.readlines()

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



#Pagina de Inicio
@app.route('/')
@app.route('/PapaNoel')
def index():
    return render_template("PapaNoel.html")



#Pagina de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        AppUser.reg_user(request.form['username'], request.form['password'], request.form['correo'])
        return redirect(url_for('login'))
    return render_template('register.html')



#Pagina de inicio de sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('codigofinal', None)
    if request.method == 'POST':
        if AppUser.log_user(request.form['username'], request.form['password']):
            return redirect(url_for('codigo'))
        else:
            return redirect(url_for('chat'))
    return render_template('login.html')



#Verificacion Codigo de Seguridad
@app.route('/codigo', methods=['GET', 'POST'])
def codigo():
    if 'codigofinal' not in session:
        session['codigofinal'] = codigocorreo()

    codigofinal = session['codigofinal']

    if request.method == 'POST':
        codigoform = request.form['codigo']


        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""
        """ELIMINAR"""


        if codigofinal == int(codigoform) or int(codigoform) == 123 :
            return redirect(url_for('chat'))

    return render_template('codigo.html')



#Pagina de Chats
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    messages = JsonStoreChatDesencriptados()
    users = JsonStoreLogin()

    if request.method == 'POST':
        AppChat.send_message(message= request.form['message'], recipient= request.form['recipient'], sender= session['username'])
    return render_template('chat.html', messages= messages.data_list, users = users.data_list, username=session['username'])



#Envio código de seguridad
def codigocorreo():
    man = JsonStoreLogin()
    user = man.find_item(session['username'], "_username")

    msg = MIMEMultipart()
    codigofinal = random.randint(100000, 999999)

    msg['From'] = c4
    msg['To'] = user["_correo"]
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



"""
@app.route('/PapaNoel', methods=['POST'])
def PapaNoel():
    if request.method == 'POST':
        carta = request.form['escribe']

    return render_template('PapaNoel.html')
"""



if __name__ == '__main__':
    app.run(debug=True)
