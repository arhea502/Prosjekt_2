# APP.PY

## Konfigurasjon

```python
app = Flask(__name__)
```
Lager Flask-appen. `__name__` brukes til å finne hvilken filens modulstil, og gjør at Flask vet hvor den finner `templates` og `static`-mapper.

---

```python
app.config['SECRET_KEY'] = '108158379'
```
Brukes til å signere session cookies. Innlogging fungerer ikke uten denne nøkkelen.

---

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
```
Forteller hvilken database Flask bruker. Her brukes SQLite, og databasen vil lagres i filen `database.db`. De tre skråstrekene `///` betyr at stien er relativ til prosjektmappen.

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
(`LoginManager(app)`) kobler Flask til login-systemet. Dette gjør at `current_user` blir tilgjengelig i alle ruter. Dette hjelper med åhåndtere session cookies og vite hvem som er logget inn.

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

Login_manager er et object fra et bibliotek som styrer innlogning, og user_loader er en calbackfunksjon som flask trenger. Når en bruker allerede er logget in lagrer flask user_id og senere når den trenger id-en igjen så sier den bare "Gi meg brukeren med denne user-id

Denne funksjonen lar flask_login hente brukere fra databasen. Den kalles automatisk ved hver forespørsel som bruker session-cookies med bruker-ID. Funksjonen henter brukeren fra databasen (`return User.query.get`) og konverterer cookie-ID-en til heltall (`int(user_id)`) siden ID-en i databasen er et heltall, og user_id ofte er en string.

---


# User model
```python
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True,  nullable=False)
    password_hash = db.Column(db.String(200),                  nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
```

Dette er en database model. Alt som refererer til (`db.model`) er database model der (`db.column`) er en rad i en table. (`Usermixin`) er noe som brukes ved innlogning-systemer i flask.  Meninga er å kunne legge ting i databaen hvor sqlite gjør alt bak kulisenet uten at du trenger å gjøre det manuelt. Alt ligger i vanlig database rader som id, username, password og om det er amin. Db.int, db.sting og db boolean definerer hva slags datatype det skal legges inn i databasen. (`primary_key`) er sånn at id-er blir skrevet unikt nedover automatisk som 1, 2, 3 ogsv. Unique betyr at det ikke kan være samme username flere ganger. (`Nullable`) betyr at feltet ikke kan være tomt. (200) og (80) er varchar, det er for at det skal være et begrenset mengde bokstaver brukt så databasen ikke larger så mye. På (`is_admin`) så er default false of boolean fordi ingen skal kunne bli admin uten grunn.