# APP.PY – Dokumentasjon

Dokumentasjon av Flask-appens konfigurasjon, innloggingssystem og databasemodeller.

---

## Innhold

- [Konfigurasjon](#konfigurasjon)
- [Flask-Login](#flask-login)
- [Databasemodeller](#databasemodeller)
  - [User](#user)
  - [Section](#section)
  - [Topic](#topic)
  - [LearningElement](#learningelement)
  - [Progress](#progress)
  - [OpenAnswer](#openanswer)
  - [TopicVisit](#topicvisit)
  - [Total databasestruktur](#total-databasestruktur)
- [Admin-oppsett](#admin-oppsett)
- [@admin\_required Decorator](#admin_required-decorator)
- [Ruter](#ruter)
  - [Login](#login-rute)
  - [Register](#register-rute)
  - [Logg ut](#logg-ut-rute)
  - [Index](#index-rute)
  - [Section](#section-rute)

---

## Konfigurasjon

> Setter opp Flask-appen, databasetilkobling og hemmelig nøkkel for session-håndtering.

```python
app = Flask(__name__)
```

Lager Flask-appen. `__name__` brukes til å finne filens modulstil, og gjør at Flask vet hvor den finner `templates`- og `static`-mapper.

---

```python
app.config['SECRET_KEY'] = '108158379'
```

Brukes til å signere session cookies. Innlogging fungerer ikke uten denne nøkkelen.
Uten en `SECRET_KEY` kan brukere i teorien manipulere session-data.

> **Session cookies** er midlertidige filer som brukes av nettsider for å huske informasjon om deg mens du navigerer fra side til side i løpet av ett enkelt besøk. De lagrer informasjon om brukeren (for eksempel innloggingsstatus) mellom forespørsler til serveren.

---

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
```

Forteller hvilken database Flask bruker. Her brukes SQLite, og databasen lagres i filen `database.db`. De tre skråstrekene `///` betyr at stien er relativ til prosjektmappen.

Dette kalles en URI (Uniform Resource Identifier), som er en standard måte å beskrive hvor en ressurs (her: database) befinner seg og hvordan man kobler til den.

---

```python
db = SQLAlchemy(app)
```

Kobler Flask til databasen, slik at databasen blir tilgjengelig overalt i appen.

SQLAlchemy er en `ORM (Object Relational Mapper)`, som betyr at du kan jobbe med databasen ved å bruke Python-klasser i stedet for rå SQL.

Eksempel:

```python
User.query.all()       # ORM
SELECT * FROM user;    # Rå SQL
```

---

## Flask-Login

> Setter opp innloggingssystemet og definerer hvordan Flask henter og gjenkjenner innloggede brukere.

```python
login_manager = LoginManager(app)
```

Kobler Flask til login-systemet. Dette gjør at `current_user` blir tilgjengelig i alle ruter, og hjelper med å håndtere session cookies og vite hvem som er logget inn.

---

```python
login_manager.login_view = 'login'
```

Hvis noen prøver å gå til en beskyttet side uten å være logget inn, vil de automatisk bli sendt til ruten `login`.

---

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

`user_loader` er en callback-funksjon som Flask trenger. Når en bruker allerede er logget inn, lagrer Flask `user_id`, og når den trenger ID-en igjen sier den bare: *"Gi meg brukeren med denne user_id."*

Funksjonen lar `flask_login` hente brukere fra databasen. Den kalles automatisk ved hver forespørsel som bruker session-cookies med bruker-ID. Den henter brukeren fra databasen (`return User.query.get`) og konverterer cookie-ID-en til heltall (`int(user_id)`), siden ID-en i databasen er et heltall og `user_id` ofte er en string.

---

## Databasemodeller

> Definerer strukturen til databasen. Hver klasse tilsvarer én tabell, og hver `db.Column` tilsvarer én kolonne i den tabellen.

---

### `User`

> Lagrer alle brukere i systemet, både vanlige brukere og admins.

```python
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True,  nullable=False)
    password_hash = db.Column(db.String(200),               nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
```

Dette er en databasemodell. Alt som arver fra `db.Model` er en databasemodell, der `db.Column` definerer en kolonne i en tabell. `UserMixin` brukes ved innloggingssystemer i Flask.

Meningen er å kunne legge ting i databasen, hvor SQLite gjør alt bak kulissene uten at du trenger å gjøre det manuelt. Alt ligger i vanlige databaserader som `id`, `username`, `password` og om det er admin.

| Attributt | Type | Forklaring |
|---|---|---|
| `id` | `db.Integer` | Heltall. `primary_key=True` gjør at ID-er skrives unikt nedover automatisk (1, 2, 3 …) |
| `username` | `db.String(80)` | Tekst, maks 80 tegn. `unique=True` betyr at samme brukernavn ikke kan brukes to ganger |
| `password_hash` | `db.String(200)` | Tekst, maks 200 tegn. Passord lagres som en hash, så de vises aldri i klartekst |
| `is_admin` | `db.Boolean` | True/False. `default=False` betyr at ingen blir admin uten grunn |

`db.Integer`, `db.String` og `db.Boolean` definerer hva slags datatype som skal legges inn i databasen. `nullable=False` betyr at feltet ikke kan være tomt. Tallene i parentes `(80)` og `(200)` fungerer som `VARCHAR` i SQL: de begrenser antall tegn slik at databasen ikke lagrer unødvendig mye.

**Eksempel i databasen:**

| id | username | password_hash | is_admin |
|----|----------|---------------|----------|
| 1  | ola      | `(hash)`      | False    |
| 2  | kari     | `(hash)`      | True     |

---

### `Section`

> Lagrer de overordnede seksjonene i læringsplattformen – det øverste nivået i innholdshierarkiet.

```python
class Section(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    emoji       = db.Column(db.String(10))
    topics      = db.relationship('Topic', backref='section', lazy=True,
                                  cascade='all, delete-orphan')
```

Denne tabellen er for seksjoner innenfor læringsplattformen. Akkurat som `User` har den `id`, `title` og `description`. Noe som er annerledes er at den bruker både `String(100)` og `Text`.

`String` og `Text` er begge datatyper i databasen. Forskjellen er at `String` har en maks lengde (for eksempel 100 tegn), mens `Text` brukes for lengre tekst uten en fast lengdebegrensning. `String` brukes ofte til korte tekster som brukernavn, e-post og titler, mens `Text` brukes til lengre innhold som beskrivelser.

I `topics` er det en `db.relationship` som connecter tabeller sammen. En section skal ha sub-sections, altså topics innenfor en section. Eksempel: *Nettverk → IP-adresse*.

| Parameter | Forklaring |
|---|---|
| `backref='section'` | Lager en reverse connection, så man kan gå fra en topic og tilbake til seksjonen den tilhører. Backref er ikke noen kobling, kun navigasjon slik at man kan gå fra child tilbake til parent – uten å endre på databasestrukturen. |
| `lazy=True` | Bestemmer hvordan data loades fra databasen. Når den er `True`, loades topics kun når du faktisk aksesserer dem. |
| `cascade='all, delete-orphan'` | Sørger for at det ikke finnes foreldreløse topics. Når du sletter en section, slettes alle topics innenfor den med. Gjelder alle cascade-operasjoner (save, change, delete). Topics kan også slettes individuelt uten å slette hele seksjonen. |

Basically betyr det:

> *"En section har mange topics. Hver topic vet hvilken section den tilhører. Når en section blir fjernet, blir topics fjernet med. Når en topic er fjernet fra en section, er den fjernet helt."*

```
Section (1)
   ├── Topic A
   ├── Topic B
   └── Topic C

Delete Section  →  sletter A, B og C
Remove Topic B  →  Topic B slettes
```

---

### `Topic`

> Lagrer undertemaer innenfor en section – det midterste nivået i innholdshierarkiet.

```python
class Topic(db.Model): 
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    elements   = db.relationship('LearningElement', backref='topic', lazy=True,
                                 cascade='all, delete-orphan')
```

`Topic`-klassen er samme som `Section`, bare at denne har `db.relationship` med `LearningElement`. Planen er jo at det er en læringsnettside med ulike seksjoner, ulike topics og ulike oppgaver.

En annen viktig ting er `db.ForeignKey('section.id')`. Dette er koden som faktisk kobler sammen section og topic. Alle sections har en `primary_key` ID i databasen, og `section_id = ForeignKey('section.id')` gjør sånn at hver topic som blir lagt innenfor en section får en `section_id` tildelt som er det samme som databasens `section.id`.

---

### `LearningElement`

> Lagrer selve innholdet i et topic – enten tekst, quiz eller åpne spørsmål.

```python
class LearningElement(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    topic_id       = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    type           = db.Column(db.String(20),  nullable=False)
    content        = db.Column(db.Text)
    question       = db.Column(db.Text)
    option_a       = db.Column(db.String(200))
    option_b       = db.Column(db.String(200))
    option_c       = db.Column(db.String(200)) 
    option_d       = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))
    answer_key     = db.Column(db.Text)
```

Denne koden sier noe om hvor læringselementer skal lagres. Det er ikke visningen eller logikken av oppgavene selv, men bare lagring.

Kolonnen `type` sier noe om hvilken type læringselement det er. Dataene tolkes ulikt avhengig av verdien her.

#### Kolonner

| Kolonne | Type | Brukes av |
|---|---|---|
| `id` | `db.Integer` | Alle |
| `topic_id` | `db.Integer` (FK) | Alle |
| `type` | `db.String(20)` | Alle, styrer tolkningen |
| `content` | `db.Text` | `text` |
| `question` | `db.Text` | `quiz` |
| `option_a` – `option_d` | `db.String(200)` | `quiz` |
| `correct_answer` | `db.String(1)` | `quiz` |
| `answer_key` | `db.Text` | Åpne spørsmål |

#### Slik tolkes `type`

**`type = "text"`** – læringselement med tekstinnhold:

```python
LearningElement(
    type="text",
    content="Dette er en forklaring"
)
```

| type | content | question | option_a |
|------|---------|----------|----------|
| text | "Dette er..." | NULL | NULL |

---

**`type = "quiz"`** – flervalgsoppgave:

```python
LearningElement(
    type="quiz",
    question="Hva er 2 + 2?",
    option_a="3",
    option_b="4"
)
```

| type | content | question | option_a | option_b |
|------|---------|----------|----------|----------|
| quiz | NULL | "Hva er 2+2?" | "3" | "4" |

---

Den ferdige strukturen ser slik ut:

```
Nettverk → IP-adresse → Quiz / Åpen spørsmål / Description
```

På grunn av `backref='section'` kan man gå baklengs også.

---

### `Progress`

> Lagrer om en bruker har svart riktig eller feil på et læringselement.

```python
class Progress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    correct    = db.Column(db.Boolean)
```

Denne koden er ganske rett fram. Den har egen `id`. Den lager en `user_id` bassert på database `user.id`-en som er i bruk. `element_id` tar den fra `learning_element` id-en for å kunne se hvilken læringselement det gjelder. `correct` er True/False for å se om svaret er riktig eller feil.

> **(FK)** betyr Foreign Key, altså kobling til en annen tabell.

| Kolonne | Type | Forklaring |
|---|---|---|
| `id` | `db.Integer` | Primærnøkkel |
| `user_id` | `db.Integer` (FK) | Peker til `user.id` – hvilken bruker det gjelder |
| `element_id` | `db.Integer` (FK) | Peker til `learning_element.id` – hvilket læringselement det gjelder |
| `correct` | `db.Boolean` | `True` hvis svaret er riktig, `False` hvis feil |

**Eksempel i databasen:**

| id | user_id | element_id | correct |
|----|---------|------------|---------|
| 1  | 1       | 5          | True    |
| 2  | 1       | 6          | False   |
| 3  | 2       | 5          | True    |

Som du kan se har 2 brukere gjort samme oppgave riktig, men bruker 1 gjorde 2 oppgaver og fikk en av dem feil.

---

### `OpenAnswer`

> Lagrer brukerens tekstsvar på åpne spørsmål, uten å vurdere om det er riktig eller feil.

```python
class OpenAnswer(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    answer     = db.Column(db.Text)
```

Denne tabellen er ganske lik `Progress`. Eneste forskjell er at istedet for at den lagrer om svaret er riktig eller ikke, så lagrer den bare svaret du gir. Fordi det er en åpen oppgave.

| Kolonne | Type | Forklaring |
|---|---|---|
| `id` | `db.Integer` | Primærnøkkel |
| `user_id` | `db.Integer` (FK) | Peker til `user.id` – hvilken bruker det gjelder |
| `element_id` | `db.Integer` (FK) | Peker til `learning_element.id` – hvilket læringselement det gjelder |
| `answer` | `db.Text` | Svaret brukeren skrev inn |

**Eksempel i databasen:**

| id | user_id | element_id | answer |
|----|---------|------------|--------|
| 1  | 1       | 6          | "Dette er mitt svar" |
| 2  | 2       | 6          | "Jeg skrev noe annet" |

Her kan du senere hente alle svar til et læringselement og evaluere dem manuelt eller via kode.

---

### `TopicVisit`

> Lagrer hvilke topics en bruker har besøkt – brukes til å spore fremgang i innholdshierarkiet.

```python
class TopicVisit(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
```

Dette er en enkel kode som sier hvilke topics brukeren har besøkt. Det gjør den ved å referere til `user.id` og `topic.id` som er i bruk der og da.

| Kolonne | Type | Forklaring |
|---|---|---|
| `id` | `db.Integer` | Primærnøkkel |
| `user_id` | `db.Integer` (FK) | Peker til `user.id` – hvilken bruker det gjelder |
| `topic_id` | `db.Integer` (FK) | Peker til `topic.id` – hvilket topic som ble besøkt |

---

## Total databasestruktur

> Oversikt over alle tabeller og hvordan de henger sammen via relasjoner og fremmednøkler.

### Innholdshierarki

```
INNHOLDSHIERARKI
════════════════════════════════════════════════════════════════════════

+-----------+         +-----------+         +-------------------+
|  Section  |         |   Topic   |         | LearningElement   |
+-----------+         +-----------+         +-------------------+
| id (PK)   |1      * | id (PK)   |1      * | id (PK)           |
| title     +-------->| title     +-------->| topic_id (FK)     |
| description         | section_id (FK)     | type              |
| emoji     |         |           |         | content           |
|           |         | .section  |<--------| question          |
|           |         | (backref) |         | option_a/b/c/d    |
| .topics   |<--------+           |         | correct_answer    |
| (backref) |         | .elements |<--------| answer_key        |
+-----------+         | (backref) |         |                   |
                      +-----------+         +-------------------+
```

### Brukersporing

```
BRUKERSPORING
════════════════════════════════════════════════════════════════════════

                      +-----------+
                      |   User    |
                      +-----------+
                      | id (PK)   |
                      | username  |
                      | password_hash
                      | is_admin  |
                      +-----------+
                       1 |  | 1  | 1
           +-----------+ |  |    +-------------+
           |             |  |                  |
           | *           |  | *                | *
+---------------+  +---------------+  +---------------+
|   Progress    |  |  OpenAnswer   |  |  TopicVisit   |
+---------------+  +---------------+  +---------------+
| id (PK)       |  | id (PK)       |  | id (PK)       |
| user_id (FK)  |  | user_id (FK)  |  | user_id (FK)  |
| element_id(FK)|  | element_id(FK)|  | topic_id (FK) |
| correct       |  | answer        |  +-------+-------+
+-------+-------+  +-------+-------+          |
        |                  |                  |
        | Kobles til       | Kobles til       | Kobles til
        | LearningElement  | LearningElement  | Topic
        +------------------+                  |
                  |                           |
                  v                           v
        +-------------------+         +-----------+
        | LearningElement   |         |   Topic   |
        | (se over)         |         | (se over) |
        +-------------------+         +-----------+
```

### Nøkkelforklaringer

```
NØKKELFORKLARINGER
════════════════════════════════════════════════════════════════════════
  PK       = Primary Key (unik identifikator per rad)
  FK       = Foreign Key (peker til PK i en annen tabell)
  backref  = automatisk omvendt referanse via SQLAlchemy
  1      * = én-til-mange-relasjon
```

---

## Admin-oppsett

> Oppretter alle databasetabeller ved oppstart, og legger til en standard admin-bruker hvis den ikke allerede finnes.

```python
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        ))
        db.session.commit()
```

`with app.app_context():` handler om at Flask trenger en "applikasjonskontekst" for å vite hvilken app som brukes når du jobber med databasen. Dette gjør sånn at databasen kan brukes uten en HTTP-forespørsel. Uten denne vil for eksempel `db.create_all()` ikke vite hvor databasen er.

`db.create_all()` lager alle tabellene som er definert med `db.Model` fra tidligere. Nå er tabellene `User`, `Topic`, `Section` osv faktisk opprettet.

`User.query.filter_by(username='admin').first()` sjekker om det allerede finnes en bruker med brukernavn `"admin"`. `filter_by` lager en SQL WHERE-klausul som filtrerer rader, og `first()` henter første rad eller `None` hvis den ikke finnes.

`db.session.add(User(...))` legger til et nytt objekt (`User`) i databasen. Det er ikke lagret ennå – det er bare midlertidig i "session".

`db.session.commit()` er det som faktisk lagrer det du legger til.

Innenfor `session.add(User(...))` finner du tabellene vi lagde i `User`-modellen: `username`, `password_hash` og `is_admin`. `username` og `is_admin` er ganske rett frem. `password_hash` er litt annerledes – her har vi satt den til `"admin123"`, men pakket inn i `generate_password_hash`. Det er noe Flask/Werkzeug-biblioteket bruker for å sjekke passord når noen logger inn.

---

## `@admin_required` Decorator

> Definerer hvor admin kreves. Man legger `@admin_required` over en route, og den gir bare tilgang til brukere med admin-privilegier. Ellers sendes brukeren til error 403 – "Forbidden" – det vil si at handlingen du prøver å utføre ikke er tillatt.

```python
from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

### Hvordan det fungerer

Denne koden lager en decorator, som tar inn en annen funksjon `f` som argument. `f` er funksjonen du ønsker å beskytte, for eksempel `admin_panel`, som bare admin skal ha tilgang til.

| Del | Forklaring |
|-----|-----------|
| `@wraps(f)` | Bevarer navnet og docstringen til originalfunksjonen `f`. Flask bruker dette for routing og debugging. Uten `wraps` vil Python tro at funksjonen heter `decorated`, selv om den egentlig representerer en annen funksjon. |
| `@login_required` | Sørger for at brukeren må være logget inn før funksjonen kjøres. Ikke-innloggede brukere sendes til `login_manager.login_view`, som er satt til `'login'`. |
| `def decorated(*args, **kwargs)` | Lager en ny funksjon som pakker inn `f`. `*args` tar imot posisjonelle argumenter, og `**kwargs` tar imot navngitte argumenter. Dette gjør at dekoratoren kan sende alle typer input videre til funksjonen, uansett hvilke argumenter den opprinnelig krever. |
| `if not current_user.is_admin: abort(403)` | Sjekker om brukeren har admin-privilegier. Hvis ikke, stoppes funksjonen og en 403 Forbidden returneres. |
| `return f(*args, **kwargs)` | Kjør originalfunksjonen `f` med alle argumentene som Flask sendte inn. |
| `return decorated` | Returnerer den nye funksjonen (`decorated`), som erstatter originalfunksjonen. Den sørger for at innlogging og admin-sjekk skjer før originalfunksjonen kjøres. |

> `*args` og `**kwargs` gjør at dekoratoren kan ta imot alle argumenter fra Flask, uten å vite på forhånd hva funksjonen trenger. Dette kan være verdier fra URL-en, query-parametere eller andre inputs.

---

### Hva er `*args` og `**kwargs`?

- `*args` samler alle posisjonelle argumenter funksjonen får.
- `**kwargs` samler alle navngitte argumenter funksjonen får.
- De gjør at dekoratoren fungerer uansett hvilke argumenter den beskyttede funksjonen trenger – du trenger ikke vite det på forhånd.

**Eksempel:**

```python
def admin_panel(id, action):
    return f"Admin {id} gjør {action}"
```

Hvis Flask sender `id=5` og `action="delete"`, vil dekoratoren motta:

```python
args = (5,)
kwargs = {'action': 'delete'}
```

Da kan den kalle originalfunksjonen med:

```python
f(*args, **kwargs)  # => admin_panel(5, action='delete')
```

**Hvorfor det er viktig:**

Flask sender parameterne fra URL eller form til funksjonen. Dekoratoren må videreformidle disse til originalfunksjonen. Uten `*args` og `**kwargs` måtte du hardkode hvilke argumenter dekoratoren tar imot, noe som gjør den lite fleksibel.

Uten `*args` og `**kwargs`:

```python
def decorated(id):  # Hva om admin_panel plutselig trenger 2 argumenter?
    ...
```

Da vil dekoratoren feile hvis funksjonen du dekorerer endrer signatur.

**Kort sagt** – `*args` og `**kwargs` gjør at dekoratoren:

1. Kan pakke inn hvilken som helst funksjon, uansett hvilke argumenter den tar.
2. Kan sende alle argumenter videre til originalfunksjonen.
3. Holder koden fleksibel og gjenbrukbar.

---

### Visualisering

Tenk at du har dette:

```python
@app.route("/admin/<int:id>")
@admin_required
def admin_panel(id):
    return f"Admin {id}"
```

Når Python ser `@admin_required`, gjør den egentlig:

```python
admin_panel = admin_required(admin_panel)
```

- `f` blir satt til originalfunksjonen (`admin_panel`)
- Dekoratoren lager `decorated`, som nå er funksjonen Flask faktisk kaller når noen besøker `/admin/<id>`

#### Når siden kalles

URL:

```
/admin/5
```

Flask gjør:

```python
decorated(5)
```

Da er:

```python
args = (5,)
kwargs = {}
```

Inni dekoratoren:

```python
return f(*args, **kwargs)
```

Blir:

```python
admin_panel(5)
```

- `decorated` kjører først sjekken om brukeren er innlogget og admin
- Deretter kjører den originalfunksjonen med samme input som Flask sendte (`id=5` i dette tilfellet)
- `*args` pakker ut posisjonelle argumenter, og `**kwargs` pakker ut navngitte argumenter

---

### Kobling til databasen

Hvis du har en database med brukere:

| Id | Username | Password | IsAdmin |
|----|----------|----------|---------|
| 1  | admin    | hsh      | True    |
| 2  | ola      | xyz      | False   |

- Bruker med `Id=1` går til `/admin/1`
  - Flask kaller `decorated(1)`
  - `current_user.is_admin` = `True` → kjører `admin_panel(1)`
- Bruker med `Id=2` går til `/admin/2`
  - `current_user.is_admin` = `False` → 403 Forbidden

> **Viktig:** `*args` og `**kwargs` inneholder input fra Flask, ikke `current_user`. Admin-sjekken bruker `current_user` for å avgjøre privilegier, uavhengig av hva som sendes i URL-en.

---

### Flytdiagram

```python
admin_panel = admin_required(admin_panel)  # admin_panel blir decorated

admin_panel(5)  # faktisk: decorated(5)
                # 1. sjekk innlogging
                # 2. sjekk admin
                # 3. hvis OK → f(5) = original admin_panel(5)
```

- `decorated` = wrapper-funksjon
- `f` = originalfunksjonen
- `decorated` returnerer resultatet fra `f`, men er fortsatt en egen funksjon
- `@wraps(f)` sørger for at navnet og docstringen til `f` beholdes

---

## Ruter

---

### Login-rute

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Feil brukernavn eller passord', 'error')
    return render_template('login.html')
```

`@app.route('/login', methods=['GET', 'POST'])` lager en rute `/login` som kan håndtere både GET (vis siden) og POST (send data fra skjema. I dette tilfellet når du trykker "logg inn"-knappen).

`if request.method == 'POST':` sjekker om brukeren har trykket på "logg inn" og sendt skjema.

`user = User.query.filter_by(username=request.form['username']).first()` – variabelen `user` blir resultatet av et søk i `User`-tabellen, der vi filtrerer på kolonnen `username` og finner brukeren som har samme brukernavn som det som ble skrevet i HTML-skjemaet. Deretter tar vi det første resultatet som matcher.

`if user and check_password_hash(user.password_hash, request.form['password']):` sjekker 2 ting: om brukernavnet finnes i databasen, og om passordet du skrev matcher brukernavnet.

Hvis det er riktig logges du inn med `login_user(user)` og blir redirecta til `/index`. Ellers vil `flash` sende en melding tilbake til siden. `flash` er en innebygd Flask-funksjon som lagrer en midlertidig melding i session, slik at den kan vises i HTML-templaten én gang for eksempel *"Feil brukernavn eller passord"*.

Når det gjelder `return` så er det en `return` per funksjonskall. Så det er enten `return render_template('index.html')` eller `return render_template('login.html')`. Ikke begge.

#### Flyt

```
Bruker åpner /login (GET)
        ↓
Vis login-skjema
        ↓
Bruker fyller ut skjema → trykker login (POST)
        ↓
Hent username fra skjema
        ↓
Søk i databasen etter brukeren
        ↓
Fant bruker?
   ┌────Ja────┐
   ↓           
Sjekk passord
   ↓
Passord riktig?
   ┌────Ja────────────────────────────┐
   ↓                                  ↓
login_user()              →   redirect til index

   Nei (feil bruker eller passord)
        ↓
flash('Feil brukernavn eller passord')
        ↓
return login.html
```

---

### Register-rute

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Brukernavnet er allerede tatt', 'error')
            return redirect(url_for('register'))
        db.session.add(User(
            username=username,
            password_hash=generate_password_hash(request.form['password']),
            is_admin=False
        ))
        db.session.commit()
        login_user(User.query.filter_by(username=username).first())
        return redirect(url_for('index'))
    return render_template('register.html')
```

Her er det bare masse kode som vi har gått gjennom tidligere, men det jeg kan si er at `if request.method == 'POST'` så kjøres hele if-setningen inni, men ellers hopper den helt til `return render_template('register.html')` fordi det er en GET method.

---

### Logg ut-rute

```python
@app.route('/logg-ut')
@login_required
def logg_ut():
    logout_user()
    return redirect(url_for('login'))
```

Den her er også ganske rett fram. Den definerer ruten logg-ut. Sier at du må være logget inn for å logge ut. Logger ut brukeren også redirecter tilbake til login.html

---

### Index-rute

```python
@app.route('/')
@login_required
def index():
    sections = Section.query.all()
    return render_template('index.html', sections=sections)
```

Denne koden definerer default ruten for index. `sections = Section.query.all()` sier at sections variabelen skal lagre samme resultat som alle sectionene som blir hentet fra tabellen Section. Dette blir tilslutt sendt til HTML.

`sections = Section.query.all()` sier at variabelen sections skal være alle items fra tabellen Section.

`return render_template('index.html', sections=sections)` Sier at den skal rerturnere templaten index og at det skal lages an ny variabel kalt sections som skal være det samme som sections variabelen vi lagde over.
Fordi den ene sections er i python og vi trenger en section svariabel i html med samme verdier. 

HTML får `sections=sections`, så i HTML kan du gjøre: `for section in sections` 

```html
<h1>Sections</h1>

<ul>
  {% for section in sections %}
    <li>
      <h2>{{ section.title }}</h2>
      <p>{{ section.content }}</p>
    </li>
  {% endfor %}
</ul>
```

---

### Section-rute

```python
@app.route('/section/<int:section_id>')
@login_required
def section(section_id):
    seksjon = Section.query.get_or_404(section_id)
    return render_template('section.html', section=seksjon)
```

Denne koden definerer hva som skjer når du går inn på en section.

`@app.route('/section/<int:section_id>')` definerer ruten i form av en variabel som er hentet fra URL-en du går til. `<int:section_id>` er den variabelen. Så URL-en blir `https://localhost:5000/section/5`. URL-en kommer fra HTML, Som får section_id fra databasen.

```html
<a href="{{ url_for('section', section_id=section.id) }}">
```
Denne html koden får section.id fra databasen når du skrev `sections=sections` tidligere i default ruten. 

Det som skjer er at brukeren trykker på en link, men før det vises i nettleser så har Jinja allerede gjort jobben.

Jinja sier `url_for('section', section_id=5)`, og Flask ser `"section"` og `section_id=5` og matcher `@app.route('/section/<int:section_id>')` som da gir resultatet `/section/5`.

Flask gjør da `section_id = 5` automatisk og kjører `section(5)`.

Etter dette gjør du `seksjon = Section.query.get_or_404(5)` som er at variabelen seksjon skal være alt fra Section databasen med id 5, ellers skal den kjøre error 404.

URL sin `section_id` kommer ikke automatisk fra databasen, MEN i praksis bruker du ofte samme verdi som finnes i databasen.

Koden sier dette:
```html
{% for section in sections %}
  <a href="/section/{{ section.id }}">
```
For hver section i sections. Skal html lage en link for /section/ ruten med /section_id.

Flask gjør **ikke** dette:
- Flask går ikke inn i databasen og henter ID-er
- Flask vet ingenting om Section-tabellen din

Flask gjør **dette**:

Når noen går til `/section/5`, sier Flask bare `section_id = 5`. Koblingen til databasen skjer når du sier `seksjon = Section.query.get_or_404(section_id)`.

``` 
DATABASE gir ID → HTML lager link → URL sender ID → Flask bruker ID → DATABASE henter igjen
1. DATABASE (har data)
2. Python backend lager HTML med url_for
3. HTML sendes til nettleser
4. bruker klikker link
5. request går til Flask
6. Flask bruker ID
7. Flask spør database

[ DATABASE ]
   id = 5
     ↓
[ HTML ]
   url_for(..., 5)
     ↓
[ URL ]
   /section/5
     ↓
[ FLASK ]
   section_id = 5
     ↓
[ DATABASE ]
   SELECT id=5
```