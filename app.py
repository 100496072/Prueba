

from cryptography.exceptions import InvalidKey
import sqlite3 as sql
import os
import datetime

from db_functions.user_functions import get_name_by_id, look_info_ban
from db_functions.chat_functions import get_chat_by_id
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from db_functions.user_functions import look_info, insert_user, set_ip, get_user_by_id
from app_cartas import send_letter
from app_mensajesdesencriptados import messages_descifrados
from app_user import reg_user, log_user
from app_chat import send_message
from attributes.attribute_pwd import AttributePwd
import attributes.attribute_user as attribute_user
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
c2 = b''
c3 = ""
c4 = ""


# Procesar cada línea del archivo
for line in lines:
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())

for line in lines:
    if line.startswith("c1"):
        c1 = eval(line.split('=')[1].strip())
    if line.startswith("c2"):
        c2 = eval(line.split('=')[1].strip())
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
        attribute_user.AttributeMensaje(request.form["escribe"])
        attribute_user.AttributeUser(request.form["name"])
        attribute_user.AttributeUser(request.form["country"])
        attribute_user.AttributeUser(request.form["city"])
        send_letter(letter=request.form["escribe"], sender=request.form["name"], correo=request.form["email"], country=request.form["country"], city=request.form["city"])
        cartascorreo(letter=request.form["escribe"], sender=request.form["name"], correo=request.form["email"], country=request.form["country"], city=request.form["city"])


    return render_template('PapaNoel.html')

#Pagina de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            AttributePwd(request.form['password1'])
            AttributePwd(request.form['password2'])
            attribute_user.AttributeUser(request.form['username'])
            if request.form['password1'] == request.form['password2']:
                try:
                    # Si la contraseña es válida, procedemos con el registro
                    info = look_info_ban(request.form['correo'])
                    if info is None:
                        if reg_user(request.form['username'], request.form['password1'], request.form['correo']):
                            return redirect(url_for('login'))
                        else:
                            print("Usuario ya existe")
                            return redirect(url_for('register'))
                    else:
                        print("Usuario vetado")
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
        AttributePwd(request.form['password'])
        attribute_user.AttributeUser(request.form['username'])
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
        attribute_user.AttributeMensaje(request.form["message"])
        attribute_user.AttributeUser(request.form["recipient"])
        send_message(message= request.form['message'], recipient= request.form['recipient'], sender= session['user_id'])

    selected_user = request.args.get('user')
    if selected_user:
        messages = messages_descifrados(selected_user, session['user_id'])

    return render_template('chat.html', messages= messages, users = users, username=get_name_by_id(session['user_id'])["username"])


@app.route("/home")
def home():
    return render_template("PapaNoel.html")

@app.route('/claves')
def claves():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, user1_id, user2_id, clave, nonce FROM chats")
    chats = cursor.fetchall()

    for chat in chats:
        chat_id = chat['id']
        encrypted_data_key = urlsafe_b64decode(chat['clave'])
        nonce_master = urlsafe_b64decode(chat['nonce'])

        # Descifrado de la clave simétrica original
        AE_Key_stma = c2  # Debes asegurarte de que `c2` esté definido previamente
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_simetrica_origen = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

        # Generar nueva clave y nonce
        nueva_clave = ChaCha20Poly1305.generate_key()
        nuevo_nonce = os.urandom(12)

        # Cifrar la nueva clave simétrica
        encrypted_nueva_clave = chacha_master.encrypt(nuevo_nonce, nueva_clave, None)

        # Convertir a base64 para almacenamiento en la base de datos
        clave_cifrada_destino = urlsafe_b64encode(encrypted_nueva_clave).decode('utf-8')
        nonce_cifrado_destino = urlsafe_b64encode(nuevo_nonce).decode('utf-8')

        # Actualizar la tabla `chats`
        cursor.execute("""
            UPDATE chats 
            SET clave = ?, nonce = ? 
            WHERE id = ?
        """, (clave_cifrada_destino, nonce_cifrado_destino, chat_id))

        # Procesar los mensajes relacionados con el chat
        cursor.execute("SELECT id, message, nonce, sender_id FROM messages WHERE chat_id = ?", (chat_id,))
        messages = cursor.fetchall()

        for mensaje in messages:
            mensaje_id = mensaje['id']
            mensajecifrado = urlsafe_b64decode(mensaje['message'])
            noncemensaje = urlsafe_b64decode(mensaje['nonce'])

            # Descifrar mensaje con clave simétrica original
            chacha_data = ChaCha20Poly1305(clave_simetrica_origen)
            mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)

            # Cifrar mensaje con la nueva clave simétrica
            nuevo_nonce_mensaje = os.urandom(12)
            chacha_nueva = ChaCha20Poly1305(nueva_clave)
            nuevo_mensaje_cifrado = chacha_nueva.encrypt(nuevo_nonce_mensaje, mensajefinal, None)

            # Convertir a base64 y obtener timestamp actual
            ct_mensaje = urlsafe_b64encode(nuevo_mensaje_cifrado).decode('utf-8')
            nonce_mensaje = urlsafe_b64encode(nuevo_nonce_mensaje).decode('utf-8')

            # Actualizar la tabla `messages`
            cursor.execute("""
                UPDATE messages 
                SET message = ?, nonce = ? 
                WHERE id = ?
            """, (ct_mensaje, nonce_mensaje, mensaje_id))

    # Guardar los cambios en la base de datos
    conn.commit()
    conn.close()

    return redirect(url_for('chat'))


@app.route("/mensajes")
def mensajescomprobacion():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    # Obtener todos los mensajes
    cursor.execute("""
        SELECT id,message, nonce, sender_id, recipient_id, chat_id
        FROM messages 
    """)
    mensajes = cursor.fetchall()

    mensajes_desencriptados = []

    for mensaje in mensajes:
        chat_id = mensaje['chat_id']
        cursor.execute("SELECT id, clave, nonce FROM chats WHERE id = ?", (chat_id,))
        chat = cursor.fetchone()

        if not chat:
            raise ValueError(f"No se encontró un chat con id {chat_id}")

        # Descifrar la clave simétrica del chat
        encrypted_data_key = urlsafe_b64decode(chat['clave'])
        nonce_master = urlsafe_b64decode(chat['nonce'])

        AE_Key_stma = c2  # Asegúrate de que `c2` esté definido previamente
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_simetrica_origen = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

        mensajecifrado = urlsafe_b64decode(mensaje['message'])
        noncemensaje = urlsafe_b64decode(mensaje['nonce'])

        # Descifrar mensaje con clave simétrica original
        chacha_data = ChaCha20Poly1305(clave_simetrica_origen)
        mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)
        mensajes_desencriptados.append({
            "id": mensaje["id"],
            "sender_id": get_name_by_id(mensaje["sender_id"])["username"],
            "recipient_id": get_name_by_id(mensaje["recipient_id"])["username"],
            "mensaje": mensajefinal.decode('utf-8')  # Convertir a texto
        })


    # Cerrar conexión
    conn.close()

    # Renderizar la plantilla con mensajes desencriptados
    return render_template("mensajes.html", mensajes=mensajes_desencriptados)

# Ruta para eliminar mensaje
@app.route('/eliminar_mensaje/<int:mensaje_id>', methods=['POST'])
def eliminar_mensaje(mensaje_id):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()

    # Eliminar el mensaje
    cursor.execute("DELETE FROM messages WHERE id = ?", (mensaje_id,))
    conn.commit()
    conn.close()

    # Redirigir a la página de mensajes
    return redirect(url_for('mensajescomprobacion'))

@app.route("/vetar")
def vetarusuarios():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    # Obtener todos los mensajes
    cursor.execute("""
        SELECT id, username, correo
        FROM users 
    """)
    usuariosto = cursor.fetchall()
    usuariostotales = []

    for user in usuariosto:
        usuariostotales.append({
            "id": user["id"],
            "username": user["username"],
            "correo": user["correo"]
        })

    # Cerrar conexión
    conn.close()
    usuariostotales = sorted(usuariostotales, key=lambda x: x['id'])

    # Renderizar la plantilla con mensajes desencriptados
    return render_template("vetar.html", usuariostotales=usuariostotales)

@app.route('/eliminar_usuario/<int:user_id>/<string:correo>,/<string:username>', methods=['POST'])
def eliminar_usuario(user_id, correo, username):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()

    # Eliminar el mensaje
    cursor.execute("DELETE FROM messages WHERE sender_id = ?", (user_id,))
    cursor.execute("DELETE FROM messages WHERE recipient_id = ?", (user_id,))
    cursor.execute("DELETE FROM chats WHERE user1_id = ?", (user_id,))
    cursor.execute("DELETE FROM chats WHERE user2_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    try:
        # Usar placeholders para insertar los valores
        cursor.execute("INSERT INTO ban (username, correo) VALUES (?,?)",
                       (username, correo))
        conn.commit()  # Guardar los cambios
        print(f"Correo '{correo}' vetado correctamente.")
    except sql.IntegrityError as e:
        print("Error al insertar:", e)  # Manejar errores de integridad

    conn.commit()
    conn.close()

    # Redirigir a la página de mensajes
    return redirect(url_for('vetarusuarios'))


if __name__ == '__main__':
    app.run(debug=True)
