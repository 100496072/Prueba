from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
        users, messages = load_data()
        if username in users:
            return 'Usuario ya registrado'
        users[username] = password, "user"
        save_data(users, messages)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users, messages = load_data()
        if username in users and users[username][0] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        return 'Credenciales incorrectas'
    return render_template('login.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    users, messages = load_data()
    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        if recipient in users:
            messages.append({'sender': session['username'], 'recipient': recipient, 'message': message})
            save_data(users, messages)
        else:
            return 'Usuario no encontrado'
    return render_template('chat.html', messages=messages, username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
