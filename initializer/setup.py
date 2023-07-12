import random

import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from random import choice, choices
from datetime import datetime, timedelta
from faker import Faker

# Connessione al database
client = MongoClient()
db = client['event_planner']

# Istanza di Faker per generare dati casuali
fake = Faker()

# Funzione per generare un ID casuale
def genera_id():
    return str(ObjectId())

# Generazione di dati casuali per le categorie degli eventi
categorie = ["Mostra", "Concerto", "Festa", "Cerimonia", "Conferenza"]

# Generazione di dati casuali per i tag degli eventi
tags = {
    "Mostra": ["arte", "pittura", "scultura"],
    "Concerto": ["musica", "live", "rock", "pop"],
    "Festa": ["feste", "divertimento", "balli"],
    "Cerimonia": ["matrimonio", "anniversario", "celebrazione"],
    "Conferenza": ["conferenze", "discorsi", "presentazioni"]
}

# Generazione di dati casuali per gli orari di inizio e fine delle attività
orari_inizio = ["09:00", "10:00", "11:00", "12:00", "13:00"]
orari_fine = ["15:00", "16:00", "17:00", "18:00", "19:00"]

# Generazione di dati casuali per le descrizioni delle spese
descrizioni_spese = ["Catering", "Noleggio attrezzature", "Servizi audiovisivi", "Decorazioni"]



import random
from datetime import datetime, timedelta

def generate_random_date():
    # Genera una data casuale tra il 1 gennaio 2000 e il 31 dicembre 2023
    start_date = datetime(2023, 5, 1)
    end_date = datetime(2023, 8, 31)

    # Calcola la differenza tra le due date
    delta = end_date - start_date

    # Genera un numero di giorni casuale all'interno dell'intervallo
    random_days = random.randint(0, delta.days)

    # Aggiungi i giorni casuali alla data di inizio per ottenere la data finale
    random_date_start = start_date + timedelta(days=random_days)

    # Genera una durata casuale tra 0 e 3 giorni
    event_duration = random.randint(0, 3)

    # Limita la durata dell'evento se necessario per evitare che siano più di 3 giorni tra la data di inizio e la data di fine
    if event_duration > (delta.days - random_days):
        event_duration = delta.days - random_days

    # Aggiungi la durata dell'evento alla data di inizio per ottenere la data di fine
    random_date_end = random_date_start + timedelta(days=event_duration)

    # Formatta le date nel formato "yyyy-mm-dd"
    formatted_start_date = random_date_start.strftime("%Y-%m-%d")
    formatted_end_date = random_date_end.strftime("%Y-%m-%d")

    return formatted_start_date, formatted_end_date



# Funzione per generare un evento casuale
def genera_evento(user_id):
    nome = fake.catch_phrase()
    categoria = choice(categorie)
    num_tags = choice(range(1, 4))  # Numero casuale di tag da selezionare
    tag = choices(tags[categoria], k=num_tags)  # Seleziona casualmente i tag dalla lista corrispondente alla categoria
    data_inizio, data_fine = generate_random_date()


    luogo = fake.address()
    informazioni_aggiuntive = fake.paragraph()

    evento = {
        "_id": genera_id(),
        "nome": nome,
        "categoria": categoria,
        "tags": tag,
        "data_inizio": data_inizio,
        "data_fine": data_fine,
        "userId": user_id,
        "budgetId": None,
        "scheduleId": None,
        "luogo": luogo,
        "informazioni_aggiuntive": informazioni_aggiuntive
    }

    return evento

# Funzione per generare un budget casuale
def genera_budget(id_evento):
    id_budget = genera_id()
    totale_spendere = 1000
    id_spese = []

    for _ in range(3):
        costo = choice([100, 200, 300, 400])
        descrizione = choice(descrizioni_spese)
        spesa = {
            "_id": genera_id(),
            "id_budget": id_budget,
            "costo": costo,
            "descrizione": descrizione
        }
        db.expenses.insert_one(spesa)
        id_spese.append(spesa["_id"])

    budget = {
        "_id": id_budget,
        "id_evento": id_evento,
        "totale_spendere": totale_spendere,
        "spese": id_spese
    }

    return budget

# Funzione per generare un'attività casuale
def genera_attivita(id_schedule):
    nome = fake.catch_phrase()
    orario_inizio = choice(orari_inizio)
    orario_fine = choice(orari_fine)

    attivita = {
        "_id": genera_id(),
        "id_schedule": id_schedule,
        "nome": nome,
        "orario_inizio": orario_inizio,
        "orario_fine": orario_fine
    }

    return attivita

# Funzione per generare un utente casuale
def genera_utente():
    email = fake.email()
    password = "password" #fake.password()
    username = fake.user_name()

    # Converto la password in un array di bytes
    bytes = password.encode('utf-8')

    # genero il salt
    salt = bcrypt.gensalt()

    # hashing
    hash = bcrypt.hashpw(bytes, salt)
    utente = {
        "_id": genera_id(),
        "email": email,
        "password": hash,
        "username": username
    }

    return utente

# Popolamento del database con dati casuali
def popola_database():
    num_utenti = 3
    num_eventi = 10
    num_attivita_per_schedule = 3

    # Genera utenti
    utenti = [genera_utente() for _ in range(num_utenti)]
    user_ids = [utente["_id"] for utente in utenti]
    db.users.insert_many(utenti)

    # Genera eventi
    eventi = []
    for _ in range(num_eventi):
        evento = genera_evento(random.choice(user_ids))
        eventi.append(evento)
        db.events.insert_one(evento)

    # Genera budget, spese e schedule per ogni evento
    for evento in eventi:
        id_evento = evento["_id"]

        # Genera budget
        budget = genera_budget(id_evento)
        evento["budgetId"] = budget["_id"]
        db.budget.insert_one(budget)
        db.events.update_one({"_id": id_evento}, {"$set": {"budgetId": budget["_id"]}})

        # Genera schedule e attività
        schedule = {
            "_id": genera_id(),
            "id_evento": id_evento,
            "activities": []
        }
        for _ in range(num_attivita_per_schedule):
            attivita = genera_attivita(schedule["_id"])
            schedule["activities"].append(attivita["_id"])
            db.activities.insert_one(attivita)
        db.schedule.insert_one(schedule)
        db.events.update_one({"_id": id_evento}, {"$set": {"scheduleId": schedule["_id"]}})

    print("Database popolato con successo!")

# Esegui la funzione per popolare il database
popola_database()