Under prøveeksamen fikk jeg spørsmålet om registering fungerte som det skulle.
da skrev jeg denne koden
```python
brukernavn = input("Skriv brukernavn: ")
passord = input("Skriv passord: ")

with app.app_context():
    users = User.query.all()
    print(users)
db.session.add(User(
    username=(brukernavn),
    password_hash= generate_password_hash(passord),
    is_admin=False
))
db.session.commit()


users = User.query.all()
print(users)

users = User.query.all()
for user in users:
     print(user.username, user.id, user.password_hash,user.is_admin)
```

Jeg klarte ikke å lage en login med HTML, så jeg endte opp med å bruke input() og variabler i stedet. Jeg skrev koden først, men fikk mange feilmeldinger.

Det første problemet var syntax-feil, der jeg hadde for mange eller for få parenteser. Men det viktigste jeg lærte var `app.app_context()`. Jeg fant ut at jeg ikke kan bruke databasen uten det, fordi Flask ikke vet hvilken applikasjon som kjører.

Derfor måtte jeg legge til `app.app_context()` for å kunne kjøre databasekode midlertidig. Etter det prøvde jeg å justere koden fram og tilbake fordi jeg ikke fikk alt til å være inni samme context.

Jeg hadde først flere separate `app.app_context()` blokker, men det skapte problemer fordi det ble for mange “øyer” og Flask ikke klarte å holde styr på det. Etter mye feilsøking og hjelp, fant jeg ut at alt som har med databasen må være i én sammenhengende context.

Jeg slet også litt med parenteser og plassering i koden, men til slutt fikk jeg det til å fungere. Jeg måtte bare rydde opp i innrykk og struktur.

Senere prøvde jeg å legge til en slette bruker funksjon ved å skrive 
```python
slett = input("Hviken bruker vil du slette: ")
def delete():
    with app.app_context():
        db.session.delete(User(
            username=(slett)
        db.session.commit()
        ))
```
Men dette var feil fordi den ikke visste hva "User" var. Så senere måtte jeg bruke `query.filter_by` for å finne frem brukeren jeg ville slette. Også skrev jeg at om den finner en user som matcher så skal den slettes. Feil koden jeg fikk var INGEN SYNTAX FEIL, men at den ikke fant variabelene jeg ønsket å finne.
Riktig versjon:
```python
slett = input("Hvilken bruker vil du slette: ")

with app.app_context():
    user = User.query.filter_by(username=slett).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        print("Bruker slettet")
    else:
        print("Bruker finnes ikke")
        ))
```
Jeg kom fram til dette med hjelp fra KI, men jeg forstår det 100% og det gir mening for meg.

---

# 📌 KI-prompter brukt i prosjektet + feilforklaring


## Prompt 1
```
users = User.query.all() print(users) db.session.add(User username='test', password_hash=generate_password_hash('test'), s_admin=False) db.session.commit print(users)
```

### ❌ Hva som var feil:
- Manglet parenteser rundt `User(...)`
- Koden var skrevet på én linje (ulovlig Python-syntaks)
- `db.session.commit` manglet `()`
- `print(users)` ble brukt uten å oppdatere data etter commit
- Ustrukturert kode (vanskelig for Python å tolke)

---

## Prompt 2
```
users = User.query.all() print(users) db.session.add(User( username='test', password_hash=generate_password_hash('test'), s_admin=False) )) db.session.commit users = User.query.all() print(users)
```

### ❌ Hva som var feil:
- Ekstra parentes `))` ga syntax error
- `db.session.commit` manglet `()`
- Ujevn struktur og feil innrykk
- Koden var ikke gyldig Python-format
- Manglende klar separasjon mellom operasjoner

---

## Prompt 3 (PowerShell / funksjonsfeil)
```
PS C:\Users\arianh\OneDrive - Osloskolen\2nd vgs\it\Prosjekt_2.5> delete(): At line:1 char:8 + delete(): + ~ An expression was expected after '('. + CategoryInfo : ParserError: (:) [], ParentContainsErrorRecordException + FullyQualifiedErrorId : ExpectedExpression
```

```
slett = input("Hvilken bruker vil du slette: ")

def delete():
    with app.app_context():
        user = User.query.filter_by(username=slett).first()

        if user:
            db.session.delete(user)
            db.session.commit()
            print("Bruker slettet")
        else:
            print("Bruker finnes ikke")
```

### ❌ Hva som var feil:
- `delete():` ble kjørt i PowerShell (ikke Python)
- PowerShell forstår ikke Python-funksjoner
- `input()` lå utenfor funksjonen (dårlig struktur)
- Funksjonen ble aldri faktisk kalt i riktig miljø
- Må kjøres i Python-runtime, ikke terminal som kommando