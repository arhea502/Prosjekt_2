# IT-Læringsplattform

> **Merk:** Denne nettsiden ble planlagt og designet ved hjelp av kunstig intelligens (KI). Jeg brukte KI som et læringsverktøy for å generere en detaljert beskrivelse av hva jeg ønsket å bygge funksjoner, struktur, og logikk og brukte dette som utgangspunkt for å forstå hva jeg trenger å lære. Målet er å gjenskape plattformen selv, steg for steg, mens jeg lærer Python, Flask og webutvikling fra bunnen av.

Målet er ikke å kunne alt sammen, eller å bli fardig, men å lære så mye som jeg kan i løpet av 8 uker.

**PS** Se (´NOTATER.md´) for å forstå hva jeg egentlig har lært. 
---

## Hva er dette?

IT-Læringsplattform er en nettbasert læringsapp bygget med Python og Flask. Den lar en administrator lage strukturert læringsinnhold som seksjoner, temaer og oppgaver som brukere kan gå gjennom for å lære IT-fag.

Plattformen støtter tre typer læringsinnhold:
- **Markdown-tekst** — forklaringer med formatert tekst, kodeeksempler og tabeller
- **Quiz** — flervalgsoppgaver med umiddelbar tilbakemelding (grønn/rød)
- **Åpne spørsmål** — fritekst-svar som lagres og kan leses av admin

Brukere får en personlig profilside som viser fremgang, quiz-resultater og hvilke temaer de har besøkt.

---

## Funksjoner

### For vanlige brukere
- Registrere og logge inn med kryptert passord
- Bla gjennom seksjoner og temaer organisert i kort
- Svare på quiz med øyeblikkelig tilbakemelding uten sidereload
- Skrive og sende inn fritekst-svar
- Se sin egen profilside med statistikk og fremdriftslinjer per tema

### For administrator
- Tilgang til et eget admin-panel
- Opprette, redigere og slette seksjoner, temaer og lærings&shy;elementer
- Forhåndsvisning av Markdown-innhold mens man skriver
- Se alle brukeres svar på quiz og åpne spørsmål
- Endre brukernavn og passord via `/admin/setup`
- Kollapsobar panel-visning som husker tilstand med localStorage

### Teknisk
- Sesjonsbasert innlogging via Flask-Login
- Passord lagres aldri i klartekst kun som hash (bcrypt via Werkzeug)
- Databasen er en enkelt SQLite-fil og opprettes automatisk ved oppstart
- Admin-kontoen opprettes automatisk (brukernavn: `admin`, passord: `admin123`)

---

## Teknologi-stack

| Teknologi | Bruk |
|---|---|
| Python 3 | Programmeringsspråk |
| Flask | Webserver og ruting |
| Flask-SQLAlchemy | Databasehåndtering |
| Flask-Login | Autentisering og sesjoner |
| Werkzeug | Passord-hashing |
| Jinja2 | HTML-malsystem (inkludert i Flask) |
| Markdown | Konverterer Markdown til HTML |
| SQLite | Database (én enkelt .db-fil) |
| HTML / CSS / JavaScript | Frontend |

---

## Filstruktur

```
laeringsplattform/
│
├── app.py                  # Hjertet i applikasjonen — ruter, modeller, logikk
│
├── templates/              # HTML-maler (Jinja2)
│   ├── base.html           # Felles layout med navbar
│   ├── login.html          # Innloggingsside
│   ├── register.html       # Registreringsside
│   ├── index.html          # Forsiden — viser alle seksjoner
│   ├── section.html        # Viser temaer i en seksjon
│   ├── topic.html          # Viser læringsinnhold i et tema
│   ├── profile.html        # Brukerens profilside med statistikk
│   └── admin/
│       ├── panel.html      # Admin-oversikt over alt innhold
│       └── setup.html      # Endre admin-brukernavn og passord
│
├── static/                 # Statiske filer (CSS, bilder, JS)
│   └── style.css           # All styling
│
└── instance/
    └── database.db         # SQLite-databasefilen (opprettes automatisk)
```

---

## Databasestruktur

Databasen har syv tabeller:

| Tabell | Innhold |
|---|---|
| `User` | Brukernavn, passordhash, admin-status |
| `Section` | Tittel, beskrivelse, emoji-ikon |
| `Topic` | Tittel, tilknyttet seksjon |
| `LearningElement` | Type (quiz/open/markdown), innhold, riktig svar |
| `Progress` | Hvem svarte hva og om det var riktig |
| `OpenAnswer` | Fritekst-svar fra brukere |
| `TopicVisit` | Registrerer hvilke temaer en bruker har besøkt |

---

## Kom i gang

### Krav
- Python 3.8 eller nyere
- pip

### Installasjon

```bash
# 1. Klon eller last ned prosjektet
cd laeringsplattform

# 2. Lag et virtuelt miljø
python -m venv venv

# 3. Aktiver det virtuelle miljøet
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Installer avhengigheter
pip install flask flask-sqlalchemy flask-login werkzeug markdown

# 5. Start appen
python app.py
```

Åpne nettleseren og gå til: **http://localhost:5000**

Logg inn som admin med:
- Brukernavn: `admin`
- Passord: `admin123`

> **Anbefalt:** Bytt passord via `/admin/setup` etter første innlogging.

---

## Læringsmål

Dette prosjektet dekker følgende konsepter:

- Grunnleggende Python-programmering
- Webserver og HTTP-ruting med Flask
- Databasemodellering og SQL med SQLAlchemy
- Autentisering, sesjoner og passord-sikkerhet
- HTML-malsystem med Jinja2 (arv, løkker, betingelser)
- Asynkron kommunikasjon mellom frontend og backend (fetch API / JSON)
- CSS-layout og responsivt design
- CRUD-operasjoner (Create, Read, Update, Delete)

---

## Status

🚧 **Under utvikling** — Prosjektet bygges aktivt mens jeg lærer. Funksjoner implementeres gradvis.

---

## Lisens

Dette er et personlig læringsprosjekt og er ikke ment for produksjonsbruk.