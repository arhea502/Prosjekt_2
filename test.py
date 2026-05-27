def si_hei():
    print("Hei!")

def si_hade():
    print("Hade!")

def kjør(f):
    print("Starter")
    f()
    print("Ferdig")

kjør(si_hei)
kjør(si_hade)
kjør

if __name__ == '__main__':
    app.run(debug=True, )
    app.run(host='0.0.0.0', port=8080,
            
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

delete()


with app.app_context():
    users = User.query.all()
    
    # Print all users
    for user in users:
        print(user.username, user.id, user.password_hash, user.is_admin)


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

delete()