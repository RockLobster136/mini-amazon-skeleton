from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, isSeller, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.isSeller = isSeller
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, isSeller, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, isSeller):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, isSeller, balance)
VALUES(:email, :password, :firstname, :lastname, :isSeller, :balance)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, 
                                  lastname=lastname, 
                                  isSeller=isSeller,
                                  balance=0)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, isSeller, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def edit(id, email, firstname, lastname):
        try:
            rows = app.db.execute("""
UPDATE Users
SET email = :email, firstname = :firstname, lastname = :lastname
WHERE id = :id
""",
                                 id = id,
                                 email = email,
                                 firstname = firstname,
                                 lastname = lastname)
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def change_password(id, password):
        rows = app.db.execute("""
UPDATE Users
SET password = :password
WHERE id = :id
""",
                              id=id,
                              password = generate_password_hash(password))
        return User.get(id)
