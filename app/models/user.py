from flask_login import UserMixin
import datetime
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, isSeller, balance, address):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.isSeller = isSeller
        self.balance = balance
        self.address = address

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, isSeller, balance, address
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
INSERT INTO Users(email, password, firstname, lastname, isSeller, balance, address)
VALUES(:email, :password, :firstname, :lastname, :isSeller, :balance, :address)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, 
                                  lastname=lastname, 
                                  isSeller=isSeller,
                                  balance=0,
                                  address = None)

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
SELECT id, email, firstname, lastname, isSeller, balance, address
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def edit(id, email, firstname, lastname, address):
        try:
            rows = app.db.execute("""
UPDATE Users
SET email = :email, firstname = :firstname, lastname = :lastname, address = :address
WHERE id = :id
""",
                                 id = id,
                                 email = email,
                                 firstname = firstname,
                                 lastname = lastname,
                                 address = address)
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

    @staticmethod
    def mgmt_fund(id, balance):
        rows = app.db.execute("""
UPDATE Users
SET balance = :balance
WHERE id = :id
""",
                              id=id,
                              balance = balance)
        return User.get(id)

    @staticmethod
    def fund_balance(uid, start, amount, category):
        num = app.db.execute("""
        SELECT COUNT(1) FROM BalanceHistory
        """
        )
        next_id = num[0][0]
        rows = app.db.execute("""
INSERT INTO BalanceHistory(id, start, amount, pid, uid, category)
VALUES(:id, :start, :amount, NULL, :uid, :category)
RETURNING id
""",
                              id = next_id,
                              start = start,
                              amount = amount,
                              uid = uid,
                              category = category)
        return rows

    @staticmethod
    def search_pur(id, search, sort_by, val_l, val_h, d_l, d_h):
        temp = f"""'%{search}%'"""
        temp_2 = f"""{sort_by}"""
        rows = app.db.execute(f"""
SELECT Pro.name as name, Pro.category as category, Pur.price as price, Pur.quantity as quantity, Pur.time_purchased as date_pur, Pur.sid as seller, Pur.order_id as order_id, Pur.order_status as order_status
FROM Purchases Pur
JOIN Products Pro
ON Pur.pid = Pro.id
WHERE Pur.uid = :id
AND Pro.name LIKE {temp}
AND Pur.price >= :val_l AND Pur.price <= :val_h
AND time_purchased >= :d_l AND time_purchased <= :d_h
ORDER BY {temp_2} DESC, order_id """
,
                              id = id,
                              val_l = val_l,
                              val_h = val_h,
                              d_l = d_l,
                              d_h = d_h)
        return rows

    @staticmethod
    def get_user_name(id):
        rows = app.db.execute("""
        SELECT CONCAT(Users.firstname, ' ', Users.lastname) AS seller_name
        FROM Users
        WHERE id = :id
        """,
        id = id)
        if len(rows)>0:
            return [row[0] for row in rows]
        else:
            return None

    @staticmethod
    def get_pur(id):
        rows = app.db.execute(f"""
SELECT Pur.id as id, Pro.name as name, Pro.category as category, Pur.price*Pur.quantity as amount, Pur.time_purchased as date_pur, Pur.order_status as order_status
FROM Purchases Pur
JOIN Products Pro
ON Pur.pid = Pro.id
WHERE Pur.uid = :id
ORDER BY Pur.time_purchased DESC"""
,
                              id = id)
        return rows

    @staticmethod
    def search_user(firstname, lastname, role):
        r = 100
        if role == "Buyer":
            r = False
        if role == "Seller":
            r = True
        if r != 100:
            switch = f""" """
        else:
            switch = f"""--"""
        if (firstname != "optional" and lastname == "optional") or (firstname == "optional" and lastname != "optional"):
            if firstname == "optional" and lastname != "optional":
                lower = lastname.lower()
                name_field = f"""lastname"""
            if firstname != "optional" and lastname == "optional":
                lower = firstname.lower()
                name_field = f"""firstname"""
            temp = f"""'%{lower}%'"""
            rows = app.db.execute(f"""
SELECT id, firstname, lastname, isseller
FROM Users
WHERE LOWER({name_field}) LIKE {temp}
{switch} AND isseller = {r}
ORDER BY id""")
            return rows
        if firstname != "optional" and lastname != "optional":
            f_name = firstname.lower()
            l_name = lastname.lower()
            temp_fn = f"""'%{f_name}%'"""
            temp_ln = f"""'%{l_name}%'"""
            rows = app.db.execute(f"""
SELECT id, firstname, lastname, isseller
FROM Users
WHERE LOWER(firstname) LIKE {temp_fn}
AND LOWER(lastname) LIKE {temp_ln}
{switch} AND isseller = {r}
ORDER BY id""")
            return rows
        return None

    @staticmethod
    def get_seller(id):
        rows = app.db.execute('''
        SELECT id, firstname, lastname, email, address
        FROM Users
        WHERE id = :id
        ''', id = id)
        return rows

    @staticmethod
    def get_seller_feedback(id):
        rows = app.db.execute('''
        SELECT rating, review, time_feedback
        FROM SellerFeedback
        WHERE sid = :id
        ''', id = id)
        return rows

    @staticmethod
    def get_balance_hist(id):
        rows = app.db.execute('''
        SELECT id, category, start, amount, start+amount as end, time_changed
        FROM BalanceHistory
        WHERE uid = :id
        ORDER BY time_changed DESC
        ''', id = id)
        return rows

    @staticmethod
    def filter_bal(uid,category,val_l,val_h,d_l,d_h):
        if category == "Purchase":
            cat = 1
        elif category == "Sell":
            cat = 2
        elif category == "Deposite":
            cat = 3
        else:
            cat = 4
        rows = app.db.execute(f"""
SELECT id, category, start, amount, start+amount as end, time_changed
FROM BalanceHistory
WHERE uid = :uid
AND category = {cat}
AND ABS(amount) >= :val_l
AND ABS(amount) <= :val_h
AND time_changed >= :d_l
AND time_changed <= :d_h
ORDER BY time_changed DESC """
,
                              uid = uid,
                              val_l = val_l,
                              val_h = val_h,
                              d_l = d_l,
                              d_h = d_h
                              )
        return rows
    @staticmethod
    def get_num_sellers():
        rows = app.db.execute(f"""
        SELECT COUNT(*)
        FROM Users
        WHERE isseller = TRUE
 """
 )
        return rows
