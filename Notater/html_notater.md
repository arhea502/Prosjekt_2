```html
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Læringsplattform{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
<nav>
  <a href="/" class="nav-logo">Læringsplattform</a>
  <div class="nav-links">
    {% if current_user.is_authenticated %}
      <a href="/">Hjem</a>
      <a href="/profil">Profil</a>
      {% if current_user.is_admin %}
        <a href="/admin" class="nav-admin">⚙️ Admin</a>
      {% endif %}
      <span class="nav-user"> {{ current_user.username }}</span>
      <a href="/logg-ut" class="nav-logout">Logg ut</a>
    {% else %}
      <a href="/login">Logg inn</a>
      <a href="/register">Registrer</a>
    {% endif %}
  </div>
</nav>
<main>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <div class="alert {{ category }}">{{ message }}</div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
</body>
</html>
```
Dette er base.html. Det er her hoversiden er. Alle andre templates bare extender denne
`  <meta name="viewport" content="width=device-width, initial-scale=1">` betyr at den skal være responsive til alle enheter.

`<title>{% block title %}Læringsplattform{% endblock %}</title>` betyr at det er standard titlen, men at andre sider kan bytte den ut. Den starter med å stå læringsplatform, men når jeg bytter side kan det bli feks: {% extends "base.html" %} 

`{% block title %}Profil{% endblock %}`

Block title er bare en tom plass man kan fylle. 
Dette gir samme layout, man slipper å kopiere html
Hver sin side får egen titel.

Alle sider arver:
navbar
layout
footer
styling
struktur

Derfor når du lager profil eller andre html sider så er det
```html
<html>
<head>
    <title>{% block title %}Læringsplattform{% endblock %}</title>
</head>
<body>

<nav>
    <a href="/">Hjem</a>
    <a href="/profil">Profil</a>
</nav>

<main>
    {% block content %}{% endblock %}
</main>

</body>
</html>
```
Base blir rammen og resten bare extender den.


`<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">``
Linker bare css til html of flask. Dette er flask versjonen av link. Man kan skrive `<link rel="stylesheet" href="/static/style.css">`, men flask versjonen er bedre fordi den fungerer uansett hvor appen ligger, funker hvis du flytter prosjektet, det er tryggere og mer fleksibel, standard Flask-praksis. `{{}}` Er jinja, pythons templaiting språk. Url_for tar en endpoint/en rute, også tar den en valgfri filnavn som parameter.


```python
<nav>
  <a href="/" class="nav-logo">Læringsplattform</a>
  <div class="nav-links">
    {% if current_user.is_authenticated %}
      <a href="/">Hjem</a>
      <a href="/profil">Profil</a>
      {% if current_user.is_admin %}
        <a href="/admin" class="nav-admin"> Admin</a>
      {% endif %}
      <span class="nav-user"> {{ current_user.username }}</span>
      <a href="/logg-ut" class="nav-logout">Logg ut</a>
    {% else %}
      <a href="/login">Logg inn</a>
      <a href="/register">Registrer</a>
    {% endif %}
  </div>
```
Alt dette er bare som python if løkker, men jinja i html. Det den gjør er at den sjekker om brukeren er logget in eller om den er admin også bestemmer den hva som skal vises basser på hvem brukeren er 

## Flash-meldinger (Jinja + Flask)

```html
<main>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <div class="alert {{ category }}">{{ message }}</div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
```

Alt inni `<main>` er det brukeren faktisk ser, fordi det er hovedinnholdet på siden.

---

### get_flashed_messages + with_categories

```jinja
{% with messages = get_flashed_messages(with_categories=true) %}
```

Dette henter alle flash-meldinger fra Flask.

`get_flashed_messages()` henter meldinger som er sendt med `flash()` i Python.

`with_categories=true` betyr at hver melding også får med en kategori/type, som f.eks. `error` eller `success`.

Eksempel i Python:

```python
flash('Brukernavnet er allerede tatt', 'error')
```

Da blir det lagret som et par:

```text
("error", "Brukernavnet er allerede tatt")
```

---

### midlertidig variabel (messages)

```jinja
messages = get_flashed_messages(...)
```

Her lagres resultatet i en midlertidig variabel som heter `messages`.

Den finnes bare inni denne `{% with %}` blokken og forsvinner etterpå.

Flash-meldinger er ikke én melding, men en liste (kø) med meldinger.

---

### for-løkken

```jinja
{% for category, message in messages %}
```

Denne går gjennom alle flash-meldingene og deler dem opp i:

```text
category = "error"
message = "Feil passord"
```

---

### visning i HTML

```html
<div class="alert {{ category }}">{{ message }}</div>
```

Dette blir til noe sånt som:

```html
<div class="alert error">Feil passord</div>
<div class="alert success">Logget inn</div>
```

---

### CSS (styling)

`alert` brukes bare for styling, og `category` bestemmer hvilken type melding det er, som kan styles forskjellig:

```css
.alert.error { color: red; }
.alert.success { color: green; }
```

---
`{% block content %}{% endblock %}`
Er bare en plassholder til andre content fra andre html.filer

## Kort oppsummert

Flash-systemet funker sånn:

- Python (`flash()`) sender meldinger med en type (error/success)
- Flask lagrer dem midlertidig i session
- Jinja (`get_flashed_messages`) henter dem
- `for`-løkke viser dem i HTML
- CSS bruker category til å style dem forskjellig

---

```html 
{% extends "base.html" %}
{% block title %}Logg inn{% endblock %}
{% block content %}
<div class="auth-wrap">
  <h1>Logg inn</h1>
  <form method="post" class="auth-form">
    <label for="username">Brukernavn</label>
    <input type="text" id="username" name="username" required autofocus>
    <label for="password">Passord</label>
    <input type="password" id="password" name="password" required>
    <button type="submit">Logg inn</button>
  </form>
  <p class="auth-alt">Ingen konto? <a href="/register">Registrer deg</a></p>
</div>
{% endblock %}
```
Denne koden extender base.html. Det betyr at den har samme layout hvor alt som har med block blir erstattet. Resten er bare html hvor h1 headeren er logg inn.

Den tar form method post altså den skal sende info over til python (Flask backend).

Label og input er koblet sammen via id og for. I label står det (`for="username"`) og i input er det (`id="username"`), dette er selve koblingen.

(`name="username"`) er det som blir sendt til backend via (`request.form i Flask`), altså det som skal hentes i Python og brukes videre i koden (for eksempel mot databasen).

**required** betyr at feltet må fylles ut før skjemaet kan sendes. Hvis brukeren prøver å sende inn uten å skrive noe, stopper nettleseren det og viser en feilmelding.

**autofocus** betyr at input-feltet automatisk blir valgt når siden lastes. Det vil si at markøren starter i feltet med en gang, så brukeren kan begynne å skrive uten å klikke først.

I skjemaet brukes ulike type-verdier for å bestemme hva slags input-felt det er:

- type="text" brukes for vanlig tekst, for eksempel brukernavn. Teksten vises helt vanlig mens du skriver.

- type="password" brukes for passordfelt. Teksten skjules mens du skriver (vises som prikker eller stjerner), slik at andre ikke kan se det.

- type="submit" brukes på knappen som sender inn skjemaet. Når brukeren trykker på denne knappen, blir hele form-en sendt til Flask (backend) via method="post".