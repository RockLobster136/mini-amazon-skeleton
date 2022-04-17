from unicodedata import category
from flask import current_app as app
class Inventory:
    def __init__(self, id, sid, pid,category,name, quantity,price,release_date,seller_firstname="",seller_lastname=""):
        self.id = id
        self.sid = sid
        self.pid = pid
        self.category = category
        self.name = name
        self.quantity = quantity
        self.price = price
        self.release_date = release_date
        self.seller_name = seller_firstname + " " + seller_lastname
    
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT I.id, I.sid, I.pid ,P.category,P.name ,I.quantity, I.price,I.release_date
FROM Inventory I, Products P
WHERE  I.pid = P.id AND I.id = :id
''',
                              id=id)
        return Inventory(*(rows[0])) if rows else None
    
    @staticmethod
    def add_inventory(sid,pid,quantity,price):
        num = app.db.execute("""
        SELECT COUNT(1) FROM Inventory
        """
        )
        next_id = num[0][0]
        try:
            rows = app.db.execute("""
INSERT INTO Inventory(id,sid, pid, quantity, price)
VALUES(:id,:sid, :pid, :quantity, :price)
RETURNING id
""",
                                  id = next_id,
                                  sid=sid,
                                  pid=pid,
                                  quantity=quantity, 
                                  price=price )
            id = rows[0][0]
            print(id)
            print(sid)
            print(Inventory.get(id).release_date)
            return Inventory.get(id)
        except Exception as e:
            print(str(e))
            return None
    @staticmethod
    def get_all_by_uid_since(sid, since):
        rows = app.db.execute('''
SELECT I.id, I.sid, I.pid ,C.name,P.name ,I.quantity, I.price,I.release_date
FROM Inventory I, Products P, Categories C
WHERE I.pid = P.id AND I.sid = :sid AND P.category = C.id
AND release_date >= :since
ORDER BY release_date DESC
''',
                              sid=sid,
                              since=since)
        return [Inventory(*row) for row in rows]
    @staticmethod
    def update_inventory(id,price,quantity):
        rows = app.db.execute("""
UPDATE Inventory
SET price = :price, quantity =:quantity
WHERE id = :id
RETURNING id
""",
                              id = id,
                              price = price,
                              quantity = quantity)
        if len(rows) > 0:
            return Inventory.get(rows[0][0])
        else:
            return None
    @staticmethod
    def delete_inventory(id):
        rows = app.db.execute("""
DELETE FROM Inventory
WHERE id = :id
RETURNING id
""",
                              id = id)
        print(rows[0][0])
        if len(rows) != 0:
            return rows[0][0]
        else:
            return None
    @staticmethod
    def get_least_n(sid,n,quantity):
            rows = app.db.execute('''
    SELECT I.id, I.sid, I.pid ,C.name,P.name ,I.quantity, I.price,I.release_date
    FROM Inventory I, Products P, Categories C
    WHERE I.pid = P.id AND I.sid = :sid AND P.category = C.id AND I.quantity < :quantity
    ORDER BY I.quantity
    LIMIT :n
    ''',
                                sid=sid,
                                n=n,
                                quantity = quantity)
            return [Inventory(*row) for row in rows]

    
    @staticmethod
    def get_sellers_for_product(pid):
        rows = app.db.execute(f'''
           SELECT Inventory.id, Inventory.sid, Inventory.pid AS pid, category, Products.name AS name, quantity, Inventory.price,
                  Inventory.release_date,  Users.firstname AS seller_firstname, Users.lastname AS seller_lastname
           FROM Inventory, Products, Users
           WHERE Inventory.pid = Products.id AND Users.id = Inventory.sid AND Inventory.pid={pid}
           ORDER BY price ASC
           ''')
        return [Inventory(*row) for row in rows]