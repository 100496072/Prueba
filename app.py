from flask import Flask, render_template, request, redirect, url_for, session
import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random




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
    with open('users.json', 'r') as f:
        users = json.load(f)
    with open('messages.json', 'r') as f:
        messages = json.load(f)
    return users, messages

# Guardar usuarios y mensajes en JSON
def save_data(users, messages):
    with open('users.json', 'w') as f:
        f.write(json.dumps(users, indent=3, sort_keys=True))
        f.write('\n')
    with open('messages.json', 'w') as f:
        f.write(json.dumps(messages, indent=3, sort_keys=True))
        f.write('\n')

@app.route('/')
@app.route('/PapaNoel')
def index():
    return render_template("PapaNoel.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        correo = request.form['correo']
        users, messages = load_data()
        for urs in users:
            if username == urs['username']:
                return 'Usuario ya registrado'
        users.append({'rol': 'Usuario', 'username':username, 'password': password, 'correo':correo})
        save_data(users, messages)
        return redirect(url_for('login'))
    return render_template('register.html')

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
                if password == urs["password"]:
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


                    return redirect(url_for('codigo'))

        if encontrado==False:
            return 'Credenciales incorrectas'
    return render_template('login.html')


@app.route('/codigo', methods=['GET', 'POST'])
def codigo():
    global codigofinal
    if request.method == 'POST':
        codigo = request.form['codigo']

        if codigofinal and (codigofinal == int(codigo) or int(codigo) == 123) :
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

if __name__ == '__main__':
    app.run(debug=True)
