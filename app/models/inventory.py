from unicodedata import category
from flask import current_app as app
class Inventory:
    def __init__(self, id, sid, pid,category,name, quantity,price,release_date):
        self.id = id
        self.sid = sid
        self.pid = pid
        self.category = category
        self.name = name
        self.quantity = quantity
        self.price = price
        self.release_date = release_date
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
        try:
            rows = app.db.execute("""
INSERT INTO Inventory(sid, pid, quantity, price)
VALUES(:sid, :pid, :quantity, :price)
RETURNING id
""",
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
    def get_all_by_uid_since(sid, since):
        rows = app.db.execute('''
SELECT I.id, I.sid, I.pid ,P.category,P.name ,I.quantity, I.price,I.release_date
FROM Inventory I, Products P
WHERE I.pid = P.id AND I.sid = :sid
AND release_date >= :since
ORDER BY release_date DESC
''',
                              sid=sid,
                              since=since)
        return [Inventory(*row) for row in rows]
    def update_inventory(sid,pid,name,price,quantity):
        rows = app.db.execute("""
UPDATE Inventory
SET price = :price, quantity =:quantity
WHERE sid = :sid AND pid = :pid
RETURNING id
""",
                              sid=sid,
                              pid=pid,
                              price = price,
                              quantity = quantity)
        return Inventory.get(rows[0][0])