import datetime

from bcrypt import hashpw, gensalt
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient

from form_logic.form import EventForm, BudgetForm, ScheduleForm, ActivityForm, ExpenseForm
from models.users import User
from models.events import Event
from models.budgets import Budget
from models.expenses import Expense
from models.schedule import Schedule
from models.activities import Activity
app = Flask(__name__, template_folder="templates")
app.secret_key = 'key'



user_model = User()
event_model = Event()
budget_model = Budget()
expense_model = Expense()
schedule_model = Schedule()
activity_model = Activity()

@app.route('/')
def index():
    # Verifica se l'utente è autenticato
    if 'user' in session:
        user_id = session['user']
        user = user_model.get_user(user_id)

        # Ottieni gli eventi associati all'utente
        events = event_model.get_all_events_by_user(user_id)

        # Mostra la home page con il calendario degli eventi
        return render_template('index.html', user=user, events=events)

    else:
        # Utente non autenticato, reindirizza alla pagina di login
        return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        psw = request.form['password']

        # Esegui l'autenticazione dell'utente
        user_id = user_model.authenticate_user(email, psw)
        if user_id:
            # Utente autenticato, salvare le informazioni nella sessione
            session['user'] = user_id
            print(session['user'])
            # Reindirizza alla pagina iniziale
            return redirect(url_for('index'))
        else:
            # Autenticazione fallita, visualizza un messaggio di errore
            error = 'Autenticazione fallita. Riprova.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user' in session:
        # Rimuovi le informazioni di autenticazione dalla sessione
        session.pop('user', None)
        # Reindirizza alla pagina di login
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verifica che le password corrispondano
        if password != confirm_password:
            error = 'Le password non corrispondono. Riprova.'
            return render_template('register.html', error=error)

        # Verifica se l'utente esiste già nel database
        user = User()
        existing_user = user.get_user_by_email(email)
        if existing_user:
            error = 'Esiste già un utente con questa email. Riprova con un altro indirizzo email.'
            return render_template('register.html', error=error)

        # Genera la password hashata
        hashed_password = hashpw(password.encode('utf-8'), gensalt())

        # Crea l'utente nel database
        user_data = {
            '_id': str(ObjectId()),
            'username': username,
            'email': email,
            'password': hashed_password
        }
        user_id = user.create_user(user_data)

        if user_id:
            # Registrazione avvenuta con successo
            session['user'] = user_id
            return redirect(url_for('index'))
        else:
            # Errore durante la registrazione, visualizza un messaggio di errore
            error = 'Errore durante la registrazione. Riprova.'
            return render_template('register.html', error=error)
    else:
        return render_template('register.html')

@app.route('/event/create', methods=['GET', 'POST'])
def create_event():
    # Estrazione dati evento
    form = EventForm(request.form)
    form.populate_user_id(session['user'])

    if request.method == 'POST' and form.validate():

        id_evento = str(ObjectId())

        #Estrazione dati budget e spese
        b_form = BudgetForm(form.budget)
        b_form.populate_evento_id(id_evento)
        id_budget = str(ObjectId())
        spese = []

        for expense_form in b_form.spese:
            e_form = ExpenseForm(expense_form)
            e_form.populate_budget_id(id_budget)

            expense_data = {
                "_id" : str(ObjectId()),
                "id_budget": e_form.id_budget.data,
                "costo" : e_form.costo.data,
                "descrizione": e_form.descrizione.data
            }
            expense_model.create_expense(expense_data)
            spese.append(expense_data.get("_id"))

        budget_data = {
            "_id" : id_budget,
            "id_evento" : b_form.id_evento.data,
            "totale_spendere" : b_form.totale_spendere.data,
            "spese" : spese
        }

        budget_model.create_budget(budget_data)

        # Estrazione dati schedule e attività
        s_form = ScheduleForm(form.schedule)
        s_form.populate_evento_id(id_evento)
        id_schedule = str(ObjectId())
        attivita = []

        for activity_form in s_form.attivita:
            a_form = ActivityForm(activity_form)
            a_form.populate_schedule_id(id_schedule)
            activity_data = {
                "_id": str(ObjectId()),
                "id_schedule": a_form.id_schedule.data,
                "nome": a_form.nome.data,
                "orario_inizio": a_form.orario_inizio.data,
                "orario_fine": a_form.orario_fine.data
            }
            activity_model.create_activity(activity_data)
            attivita.append(activity_data.get("_id"))

        schedule_data = {
            "_id" :  id_schedule,
            "id_evento" : s_form.id_evento.data,
            "activities" : attivita
        }

        schedule_model.create_schedule(schedule_data)

        event_data = {
            "_id": id_evento,
            "nome": form.nome.data,
            "categoria": form.categoria.data,
            "tags": form.tags.data,
            "data_inizio": form.data_inizio.data,
            "data_fine": form.data_fine.data,
            "userId": form.organizzatore.data,
            "budgetId": id_budget,
            "scheduleId": id_schedule,
            "luogo": form.luogo.data,
            "informazioni_aggiuntive": form.info_add.data
        }

        event_model.create_event(event_data)

        return redirect(url_for('evento_dettaglio'))
    return render_template('index.html', form=form)#todo

@app.route("/events", methods=['GET'])
def get_user_month_events():
    user = session.get('user')  # Ottieni l'utente dalla sessione
    mese = int(request.args.get('mese'))
    anno = int(request.args.get('anno'))

    # Costruisci le date di inizio e fine per il mese e anno specificati
    data_inizio = f"{anno}-{mese:02d}-01"
    data_fine = f"{anno}-{mese:02d}-31"

    event_model = Event()
    events = event_model.get_all_events_by_year_month(user, data_inizio, data_fine)

    return jsonify(list(events))

if __name__ == '__main__':
    app.run(debug=True)
