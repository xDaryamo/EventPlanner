from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from models.users import User

app = Flask(__name__)
app.secret_key = 'key'
client = MongoClient('mongodb://localhost:27017/')

user_model = User()


@app.route('/')
def index():
    if 'user' in session:
        # Utente autenticato, reindirizza alla pagina iniziale
        return redirect(url_for('home'))
    else:
        # Utente non autenticato, reindirizza alla pagina di login
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Esegui l'autenticazione dell'utente
        is_authenticate, user_id = user_model.authenticate_user(email, password)
        if is_authenticate:
            # Utente autenticato, salvare le informazioni nella sessione
            session['user'] = user_id
            # Reindirizza alla pagina iniziale
            return redirect(url_for('home'))
        else:
            # Autenticazione fallita, visualizza un messaggio di errore
            error = 'Autenticazione fallita. Riprova.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Rimuovi le informazioni di autenticazione dalla sessione
    session.pop('user', None)
    # Reindirizza alla pagina di login
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', user_id=session['user'])
    else:
        return redirect(url_for('login'))


