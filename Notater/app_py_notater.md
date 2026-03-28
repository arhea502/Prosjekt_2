# APP.PY – Dokumentasjon

---

## Konfigurasjon

```python
app = Flask(__name__)
```

Lager Flask-appen. `__name__` brukes til å finne hvilken filens modulstil, og gjør at Flask vet hvor den finner `templates`- og `static`-mapper.

---

```python
app.config['SECRET_KEY'] = '108158379'
```

Brukes til å signere session cookies. Innlogging fungerer ikke uten denne nøkkelen.

> **Session cookies** er midlertidige filer som brukes av nettsider for å huske informasjon om deg mens du navigerer fra side til side i løpet av ett enkelt besøk. De lagrer informasjon om brukeren (for eksempel innloggingsstatus) mellom forespørsler til serveren.

---

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
```

Forteller hvilken database Flask bruker. Her brukes SQLite, og databasen lagres i filen `database.db`. De tre skråstrekene `///` betyr at stien er relativ til prosjektmappen.

---

```python
db = SQLAlchemy(app)
```

Kobler Flask til databasen, slik at databasen blir tilgjengelig overalt i appen.

---

## Flask-Login + Databasemodeller

```python
login_manager = LoginManager(app)
```

`LoginManager(app)` kobler Flask til login-systemet. Dette gjør at `current_user` blir tilgjengelig i alle ruter, og hjelper med å håndtere session cookies og vite hvem som er logget inn.

---

```python
login_manager.login_view = 'login'
```

Hvis noen prøver å gå til en beskyttet side uten å være logget inn, vil de automatisk bli sendt til ruten `login`. Senere i `app.routes` forklares det hvordan dette brukes.

---

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

`login_manager` er et objekt fra et bibliotek som styrer innlogging, og `user_loader` er en callback-funksjon som Flask trenger. Når en bruker allerede er logget inn, lagrer Flask `user_id`, og når den trenger ID-en igjen sier den bare: *"Gi meg brukeren med denne user_id."*

Denne funksjonen lar `flask_login` hente brukere fra databasen. Den kalles automatisk ved hver forespørsel som bruker session-cookies med bruker-ID. Funksjonen henter brukeren fra databasen (`return User.query.get`) og konverterer cookie-ID-en til heltall (`int(user_id)`), siden ID-en i databasen er et heltall og `user_id` ofte er en string.

---

## Modeller

### `User`

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

