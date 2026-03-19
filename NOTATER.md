# APP.PY

## Konfigurasjon

- `app = Flask(__name__)`  
  Lager Flask-appen. `__name__` brukes til å finne hvilken fil som skal starte opp, og gjør at Flask vet hvor den finner `templates` og `static`-mapper.

- `app.config['SECRET_KEY'] = '108158379'`  
  Brukes til å signere session cookies. Innlogging fungerer ikke uten denne nøkkelen.

- `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'`  
  Forteller hvilken database Flask bruker. Her brukes SQLite, og databasen vil lagres i filen `database.db`. De tre skråstrekene `///` betyr at stien er relativ til prosjektmappen.

- `db = SQLAlchemy(app)`  
  Kobler Flask til databasen, slik at databasen blir tilgjengelig overalt i appen.

## Flask-Login + Databasemodeller

- `login_manager = LoginManager(app)`  
  Kobler Flask til login-systemet. Gjør at `current_user` blir tilgjengelig i alle ruter.

- `login_manager.login_view = 'login'`  
  Hvis noen prøver å gå til en beskyttet side uten å være logget inn, vil de automatisk bli sendt til ruten `login`.

- ```python
  @login_manager.user_loader
  def load_user(user_id):
      return User.query.get(int(user_id))`