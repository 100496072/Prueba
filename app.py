

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
from app_cartas import cartascorreo

from db_functions.user_functions import get_name_by_id, get_user_by_id, get_users
from db_functions.table_creation import initialize_db

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


#Pagina de Inicio
@app.route('/')


@app.route('/PapaNoel', methods=['POST'])
def PapaNoel():
    initialize_db()
    if request.method == 'POST':
        send_letter(letter=request.form["escribe"], sender=request.form["name"], correo=request.form["email"], country=request.form["country"], city=request.form["city"])
        cartascorreo(letter=request.form["escribe"], sender=request.form["name"], correo=request.form["email"], country=request.form["country"], city=request.form["city"])


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
    if request.method == 'POST':
            log = log_user(request.form['username'], request.form['password'])
            if log is True:
                return redirect(url_for('chat'))
            elif log is False:
                return redirect(url_for('codigo'))

    return render_template('login.html')



#Verificacion Codigo de Seguridad
@app.route('/codigo', methods=['GET', 'POST'])
def codigo():
    codigofinal = session["codigofinal"]

    if request.method == 'POST':
        codigoform = request.form['codigo']

        if codigofinal == int(codigoform):
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


@app.route("/home")
def home():
    return render_template("PapaNoel.html")

#Envio código de seguridad



if __name__ == '__main__':
    app.run(debug=True)
