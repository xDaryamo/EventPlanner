from wtforms import Form, StringField, DateField, DecimalField, HiddenField, TimeField, FormField, FieldList, validators
from wtforms.validators import InputRequired, Length, ValidationError

class ActivityForm(Form):
    # Definisci i campi per l'attività
    id_schedule = HiddenField()
    nome = StringField('Nome attivita', validators=[Length(max=100)])
    orario_inizio = TimeField('Orario inizio', validators=[InputRequired()])
    orario_fine = TimeField('Orario fine', validators=[InputRequired()])

    def populate_schedule_id(self, schedule_id):
        self.id_schedule.data = schedule_id

class ScheduleForm(Form):
    # Definisci i campi per la schedule
    id_evento = HiddenField()
    attivita = FieldList(FormField(ActivityForm), min_entries=0)

    def populate_evento_id(self, evento_id):
        self.id_evento.data = evento_id

class ExpenseForm(Form):
    # Definisci i campi per la spesa
    id_budget = HiddenField()
    costo = DecimalField('Costo', validators=[validators.Optional()])
    descrizione = StringField('Descrizione', validators=[InputRequired(), Length(max=255)])

    def populate_budget_id(self, budget_id):
        self.id_budget.data = budget_id

class BudgetForm(Form):
    # Definisci i campi per il budget
    totale_spendere = DecimalField('Totale', validators=[validators.Optional()])
    id_evento = HiddenField()
    spese = FieldList(FormField(ExpenseForm), min_entries=0)

    def populate_evento_id(self, evento_id):
        self.id_evento.data = evento_id

class EventForm(Form):
    nome = StringField('Nome evento', validators=[InputRequired(), Length(max=100)])
    categoria = StringField('Categoria evento', validators=[InputRequired(), Length(max=100)])
    tags = StringField('Tags', validators=[InputRequired(), Length(max=100)])
    data_inizio = DateField('Data Inizio', validators=[InputRequired()])
    data_fine = DateField('Data Fine', validators=[InputRequired()])
    organizzatore = HiddenField()
    budget = FormField(BudgetForm)
    schedule = FormField(ScheduleForm)
    luogo = StringField('Luogo', validators=[InputRequired(), Length(max=100)])
    info_add = StringField('Informazioni extra', validators=[InputRequired(), Length(max=255)])

    def populate_user_id(self, user_id):
        self.organizzatore.data = user_id

class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(max=50)])
    password = StringField('Password', validators=[InputRequired(), Length(max=50)])

class RegistrationForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(max=50)])
    password = StringField('Password', validators=[InputRequired(), Length(max=50)])
    confirm_password = StringField('Conferma password', validators=[InputRequired(), Length(max=50)])

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Le password non corrispondono.')