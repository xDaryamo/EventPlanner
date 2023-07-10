import pymongo
from bson import ObjectId
from faker import Faker

# Connessione al database MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["eventplanner"]

# Creazione delle collezioni
events_collection = database["events"]
budgets_collection = database["budgets"]
expenses_collection = database["expenses"]
schedule_collection = database["schedule"]
activities_collection = database["activities"]
users_collection = database["users"]

# Creazione di un evento
def create_event(nome, categoria, tags, data_inizio, data_fine, organizzatore_id, luogo, descrizione):
    event = {
        "_id": ObjectId(),
        "nome": nome,
        "categoria": categoria,
        "tags": tags,
        "dataInizio": data_inizio,
        "dataFine": data_fine,
        "organizzatoreId": organizzatore_id,
        "budgetId": None,
        "scheduleId": None,
        "luogo": luogo,
        "informazioniAggiuntive": descrizione

    }
    events_collection.insert_one(event)
    return event["_id"]

# Creazione di un budget per un evento
def create_budget(event_id, totale):
    budget = {
        "_id": ObjectId(),
        "eventoId": event_id,
        "totale": totale,
        "spese": None
    }
    budgets_collection.insert_one(budget)
    return budget["_id"]

# Creazione di una spesa per un budget di un evento
def create_expense(budgets_id, quantita, descrizione):
    expense = {
        "_id": ObjectId(),
        "budgetsId": budgets_id,
        "quantita": quantita,
        "descrizione": descrizione
    }
    expenses_collection.insert_one(budget)
    return expense["_id"]

# Creazione di uno schedule per un evento
def create_schedule(event_id):
    schedule = {
        "_id": ObjectId(),
        "eventoId": event_id,
        "attivita": None
    }
    schedule_collection.insert_one(activity)
    return schedule["_id"]

# Creazione di un'attività per un evento
def create_activity(schedule_id, nome_attivita, orario_inizio, orario_fine):
    activity = {
        "_id": ObjectId(),
        "scheduleId": schedule_id,
        "nomeAttivita": nome_attivita,
        "orarioInizio": orario_inizio,
        "orarioFine": orario_fine
    }
    activities_collection.insert_one(activity)
    return activity["_id"]

# Creazione di un utente organizzatore
def create_user(username, password, email):

    emails = users_collection.find({'email': email})

    if email in emails:
        return None

    user = {
        "_id": ObjectId(),
        "username": username,
        "password": password,
        "email": email
    }
    users_collection.insert_one(user)
    return user["_id"]

# Generazione di dati casuali utilizzando il modulo faker
fake = Faker()

# Creazione di utenti organizzatori
def create_fake_users(num_users):
    user_ids = []

    domains = ["gmail.com", "yahoo.com", "hotmail.com", "example.com"]  # Elenca qui i domini che desideri utilizzare
    random_domain = fake.random.choice(domains)
    user_name = fake.user_name()

    for _ in range(num_users):
        user_id = create_user(
            user_name,
            fake.password(),
            user_name + random_domain
        )
        user_ids.append(user_id)

    return user_ids

# Creazione di eventi
def create_fake_events(num_events, num_activities):
    event_ids = []
    user_ids = list(users_collection.find().distinct("_id"))

    categories = ["Mostra", "Concerto", "Festa", "Cerimonia", "Conferenza"]

    tags = {
        "Mostra": ["Arte contemporanea", "Pittura", "Scultura", "Fotografia", "Installazioni", "Esposizione",
                   "Vernissage"],
        "Concerto": ["Rock", "Pop", "Jazz", "Classica", "Elettronica", "Hip-hop", "Indie", "Festival"],
        "Festa": ["Compleanno", "Laurea", "Matrimonio", "Anniversario", "Baby shower", "Addio al celibato/nubilato",
                  "Festa a tema"],
        "Cerimonia": ["Premiazione", "Inaugurazione", "Consegna di riconoscimenti", "Cerimonia religiosa",
                      "Cerimonia di apertura/chiusura", "Cerimonia di premiazione"],
        "Conferenza": ["Business", "Tecnologia", "Salute", "Educazione", "Scienza", "Ambiente", "Marketing",
                       "Leadership"]
    }

    for _ in range(num_events):
        organizzatore_id = fake.random.choice(user_ids)

        categoria = fake.random_element(categories)
        event_id = create_event(
            fake.company(),
            categoria,
            fake.random.sample(tags[categoria], fake.random.randint(1, len(tags[categoria]))),
            fake.future_datetime(),
            fake.future_datetime(),
            organizzatore_id,
            fake.address(),
            fake.text()
        )
        event_ids.append(event_id)

        budget_id = create_budget(
            event_id,
            fake.random_int(1000, 10000),
            [{"nome": fake.word(), "importo": fake.random_int(100, 1000)} for _ in range(fake.random_int(1, 5))]
        )

        for _ in range(num_activities):
            create_activity(
                event_id,
                fake.job(),
                fake.future_datetime(),
                fake.future_datetime()
            )

    return event_ids



# Esempio di creazione di 10 utenti organizzatori
user_ids = create_fake_users(10)

# Esempio di creazione di 20 eventi con 5 attività per ogni evento
event_ids = create_fake_events(20, 5)

# Recupero degli eventi
events = events_collection.find()
for event in events:
    print(event)

# Recupero del budget per un evento specifico
budget = budgets_collection.find_one({"eventoId": event_ids[0]})
print(budget)

# Recupero delle attività per un evento specifico
activities = program_collection.find({"eventoId": event_ids[0]})
for activity in activities:
    print(activity)

# Recupero dell'utente organizzatore per un evento specifico
organizzatore = users_collection.find_one({"_id": user_ids[0]})
print(organizzatore)

# Chiusura della connessione al database
client.close()