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
        
       