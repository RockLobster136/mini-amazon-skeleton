from flask import current_app as app

class Inventory:
    def __init__(self, id, sid, pid, quantity,price,release_date):
        self.id = id
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.price = price
        self.release_date = release_date
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, sid, pid,quantity,price, release_date
FROM Purchases
WHERE id = :id
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
            return Inventory.get(id)
        except Exception as e:
            print(str(e))
            return None
