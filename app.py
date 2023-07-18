import datetime
import json

from bcrypt import hashpw, gensalt
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
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


@app.route('/insert-event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'GET':
        start_day = request.args.get('day')
        start_month = request.args.get('month')
        start_year = request.args.get('year')

        return render_template('create-event.html', giorno=start_day, mese=start_month, anno=start_year)

    if request.method == 'POST':
        id_evento = str(ObjectId())
        nome_evento = request.form['nome_evento']
        categoria = request.form['categoria']

        tags = request.form['tags']
        tags_list = [tag.strip() for tag in tags.split(',')]

        # Aggiungere i controlli sulla data
        data_inizio = request.form['data_inizio']
        data_fine = request.form['data_fine']

        luogo = request.form['luogo']
        informazioni_aggiuntive = request.form['informazioni_aggiuntive']

        include_budget = request.form.get('include_budget')
        id_budget = None

        if include_budget:
            id_budget = str(ObjectId())
            totale_spesa = request.form['totale_spesa']

            spese = []
            for key, value in request.form.items():
                if key.startswith('costo') and value:
                    spesa_num = key.replace('costo', '')
                    descrizione = request.form.get(f'descrizione{spesa_num}')
                    spesa = {
                        '_id': str(ObjectId()),
                        'id_budget': id_budget,
                        'costo': value,
                        'descrizione': descrizione
                    }
                    expense_model.create_expense(spesa)
                    spese.append(spesa['_id'])

            budget_item = {
                "_id": id_budget,
                "id_evento": id_evento,
                'totale_spendere': totale_spesa,
                'spese': spese
            }

            budget_model.create_budget(budget_item)

        include_schedule = request.form.get('include_schedule')
        id_schedule = None

        if include_schedule:
            id_schedule = str(ObjectId())
            attivita = []

            for key, value in request.form.items():
                if key.startswith('actname') and value:
                    activitiy_num = key.replace('actname', '')
                    orario_inizio = request.form.get(f'orario_inizio{activitiy_num}')
                    orario_fine = request.form.get(f'orario_fine{activitiy_num}')
                    activity = {
                        '_id': str(ObjectId()),
                        'id_schedule': id_schedule,
                        'nome': value,
                        'orario_inizio': orario_inizio,
                        'orario_fine': orario_fine
                    }

                    activity_model.create_activity(activity)
                    attivita.append(activity['_id'])

            schedule_item = {
                "_id": id_schedule,
                "id_evento": id_evento,
                'attivita': attivita
            }

            schedule_model.create_schedule(schedule_item)

        # Creazione del documento evento

        evento = {
            '_id': id_evento,
            'nome': nome_evento,
            'categoria': categoria,
            'tags': tags_list,
            'data_inizio': data_inizio,
            'data_fine': data_fine,
            'userId': session['user'],
            'luogo': luogo,
            'informazioni_aggiuntive': informazioni_aggiuntive,
            'budgetId': id_budget,
            'scheduleId': id_schedule
        }

        # Salvataggio del documento evento nel database
        event_model.create_event(evento)

    return render_template('index.html')


# Modifica di un evento
@app.route('/update-event', methods=['GET', 'POST'])
def update_event():
    if request.method == 'GET':
        event_id = request.args.get('event-id')
        event_retrieved = event_model.get_event(event_id)

        return render_template('modify-event.html', event=event_retrieved)

    if request.method == 'POST':
        event_id = request.form['event_id']
        event_retrieved = event_model.get_event(event_id)

        tags = request.form['tags']
        tags_list = [tag.strip() for tag in tags.split(',')]

        event_data = {
            'nome': request.form['nome_evento'],
            'categoria': request.form['categoria'],
            'tags': tags_list,
            'data_inizio': request.form['data_inizio'],
            'data_fine': request.form['data_fine'],
            'luogo': request.form['luogo'],
            'informazioni_aggiuntive': request.form['informazioni_aggiuntive'].strip(),
        }

        totale_spesa = 0

        if 'include_budget' in request.form:

            action = 'update'

            budget_data = {
                '_id': None,
                'id_evento': event_id,
                'totale_spendere': request.form['totale_spesa'],
                'spese': None
            }
            if event_retrieved['budgetId']:
                id_budget = request.form['budget_id']
            else:
                action = 'create'
                id_budget = str(ObjectId())

            budget_data['_id'] = id_budget

            spese = []
            for key, value in request.form.items():
                if key.startswith('costo') and value:
                    spesa_num = key.replace('costo', '')
                    descrizione = request.form.get(f'descrizione{spesa_num}')

                    spesa = {
                        '_id': None,
                        'id_budget': id_budget,
                        'costo': value,
                        'descrizione': descrizione
                    }
                    id_spesa = request.form[f'spesa_id{spesa_num}']

                    if not id_spesa:
                        spesa['_id'] = str(ObjectId())
                        expense_model.create_expense(spesa)
                        spese.append(spesa['_id'])

                    else:
                        spesa['_id'] = id_spesa
                        expense_model.update_expense(id_spesa, spesa)
                        spese.append(id_spesa)

            budget_data['spese'] = spese

            if action == 'update':
                budget_model.update_budget(id_budget, budget_data)

            else:
                budget_model.create_budget(budget_data)

            event_data['budgetId'] = budget_data['_id']

        elif event_retrieved['budgetId'] and 'include_budget' not in request.form:
            for key, value in request.form.items():
                if key.startswith('costo') and value:
                    spesa_num = key.replace('costo', '')

                    id_spesa = request.form[f'spesa_id{spesa_num}']
                    if id_spesa:
                        budget_model.remove_expense(event_retrieved['budgetId'], id_spesa)

        if 'include_schedule' in request.form:

            action = 'update'

            schedule_data = {
                '_id': None,
                'id_evento': event_id,
                'activities': None
            }

            if event_retrieved['scheduleId']:
                id_schedule = request.form['schedule_id']
            else:
                action = 'create'
                id_schedule = str(ObjectId())

            schedule_data['_id'] = id_schedule

            attivita = []

            for key, value in request.form.items():
                if key.startswith('actname') and value:
                    num_attivita = key.replace('actname', '')
                    orario_inizio = request.form.get(f'orario_inizio{num_attivita}')
                    orario_fine = request.form.get(f'orario_fine{num_attivita}')

                    act = {
                        '_id': None,
                        'id_schedule': id_schedule,
                        'nome': value,
                        'orario_inizio': orario_inizio,
                        'orario_fine': orario_fine
                    }

                    id_attivita = request.form[f'attivita_id{num_attivita}']
                    print(id_attivita)
                    if not id_attivita:
                        act['_id'] = str(ObjectId())
                        activity_model.create_activity(act)
                        attivita.append(act['_id'])

                    else:
                        act['_id'] = id_attivita
                        activity_model.update_activity(id_attivita, act)
                        attivita.append(id_attivita)

            schedule_data['activities'] = attivita

            if action == 'update':
                schedule_model.update_schedule(id_schedule, schedule_data)

            else:
                schedule_model.create_schedule(schedule_data)

            event_data['scheduleId'] = schedule_data['_id']

        elif event_retrieved['scheduleId'] and 'include_schedule' not in request.form:
            for key, value in request.form.items():
                if key.startswith('actname') and value:
                    act_num = key.replace('actname', '')
                    print(act_num)
                    id_attivita = request.form[f'attivita_id{act_num}']
                    if id_attivita:
                        schedule_model.remove_activity(event_retrieved['scheduleId'], id_attivita)

        event_model.update_event(event_id, event_data)
        return redirect(url_for('index'))


# Cancellazione di un evento
@app.route('/delete_event', methods=['GET'])
def delete_event(event_id):
    request.args.get('event-id')
    event_model.delete_event(event_id)
    return redirect(url_for('index'))


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


@app.route("/get_budget", methods=['GET'])
def get_budget():
    budget_id = request.args.get('budget-id')
    budget_retrieved = budget_model.get_budget(budget_id)

    spese = []
    if budget_retrieved:
        for spesa in budget_retrieved['spese']:
            spese.append(expense_model.get_expense(spesa))

        budget = {
            '_id': budget_retrieved['_id'],
            'id_evento': budget_retrieved['id_evento'],
            'totale_spendere': budget_retrieved['totale_spendere'],
            'spese': spese
        }

        return jsonify(budget)
    else:
        return jsonify(None)


@app.route("/get_schedule", methods=['GET'])
def get_schedule():
    schedule_id = request.args.get('schedule-id')
    schedule_retrieved = schedule_model.get_schedule(schedule_id)

    attivita = []
    if schedule_retrieved:
        for act in schedule_retrieved['activities']:
            attivita.append(activity_model.get_activity(act))

        schedule = {
            '_id': schedule_retrieved['_id'],
            'id_evento': schedule_retrieved['id_evento'],
            'activities': attivita
        }
        return jsonify(schedule)
    else:
        return jsonify(None)


@app.route("/delete_expense", methods=['GET'])
def delete_expense():
    expense_id = request.args.get('expense_id')
    budget_id = request.args.get('budget_id')

    if expense_id:
        budget_model.remove_expense(budget_id, expense_id)
        expense_model.delete_expense(expense_id)

    return jsonify({'message': 'deleted'})


@app.route("/delete_activity", methods=['GET'])
def delete_activity():
    act_id = request.args.get('activity_id')
    schedule_id = request.args.get('schedule_id')

    schedule_model.remove_activity(schedule_id, act_id)

    activity_model.delete_activity(act_id)

    return jsonify({'message': 'deleted'})


@app.route('/event-details', methods=['GET', 'POST'])
def event_details():
    if request.method == 'GET':
        event_ids = request.args.get('event-ids')
        event_ids_list = json.loads(event_ids)
        event_ids_list = json.loads(event_ids_list)

        start_day = request.args.get('day')
        start_month = request.args.get('month')
        start_year = request.args.get('year')

        events = []
        for event_id in event_ids_list:
            events.append(event_model.get_event(event_id))

        return render_template('event-details.html', events=events, day=start_day, month=start_month, year=start_year)


@app.route('/events-by-tags', methods=['GET', 'POST'])
def events_by_tag():

    if request.method == 'GET':
        user = session.get('user')
        tags = request.args.get('tags')
        events = event_model.get_all_events_by_tags(tags, user)

        return render_template('event-details.html', events=events)


if __name__ == '__main__':
    app.run(debug=True)
