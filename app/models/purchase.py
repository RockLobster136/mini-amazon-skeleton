from xml.sax.handler import property_declaration_handler
from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, sid, time_purchased, quantity, 
                            price,order_id = None,order_status= None,fulfill_date= None,
                            prodname= None,prodcat= None,proddes= None,prodimage= None,
                            buyer_address = None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.time_purchased = time_purchased
        self.quantity = quantity
        self.price = price
        self.order_status = order_status
        self.order_id = order_id
        if self.order_status:
            self.fulfill_date = fulfill_date
        else:
            self.fulfill_date = None
        self.batch_status = False
        self.prodname = prodname
        self.podcat = prodcat
        self.proddes = proddes
        self.prodimage = prodimage
        self.address = buyer_address
        self.total = self.price*self.quantity

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, sid, time_purchased, quantity, price
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Pur.id, Pur.uid, Pur.pid, Pur.sid, Pur.time_purchased, Pur.quantity,
Pur.price,order_id,order_status,fulfill_date,Pro.name,Categories.name,Pro.description,
Pro.image,U.address
FROM Purchases Pur
INNER JOIN Products Pro
ON Pur.pid = Pro.id
INNER JOIN Users U
ON Pur.uid = U.id
INNER JOIN Categories
ON Pro.category = Categories.id
WHERE Pur.uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC ,order_id
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
    @staticmethod
    def get_seller_orders(sid,since):
        rows = app.db.execute('''
SELECT Pur.id, Pur.uid, Pur.pid, Pur.sid, Pur.time_purchased, Pur.quantity,
Pur.price,order_id,order_status,fulfill_date,Pro.name,Pro.category,Pro.description,
Pro.image,U.address
FROM Purchases Pur
INNER JOIN Products Pro
ON Pur.pid = Pro.id
INNER JOIN Users U
ON Pur.uid = U.id
WHERE sid = :sid
AND time_purchased >= :since
ORDER BY time_purchased DESC ,order_id
''',
                              sid=sid,
                              since=since)
        return [Purchase(*row) for row in rows]
    @staticmethod
    def fulfill_item(id,time):
        rows = app.db.execute("""
UPDATE Purchases
SET order_status =TRUE, fulfill_date = :time
WHERE id = :id
RETURNING id
""",
                              id = id, time = time)
        if len(rows) > 0:
            return Purchase.get(rows[0][0])
        else:
            return None
    
    @staticmethod
    def delete_item(id):
        rows = app.db.execute("""
DELETE FROM Purchases
WHERE id = :id
RETURNING id
""",
                              id = id)
        print(rows)
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None

    @staticmethod
    def check_order_fulfill(oid,sid):
        rows = app.db.execute("""
SELECT order_status
FROM Purchases
WHERE order_id = :oid AND sid = :sid
""",
                              oid = oid,
                              sid = sid)
        for row in rows:
            if not row[0]:
                return False
        return True

    
    
    @staticmethod
    def get_seller_order_view(sid,oid):
        rows = app.db.execute('''
SELECT Pur.id, Pur.uid, Pur.pid, Pur.sid, Pur.time_purchased, Pur.quantity,
Pur.price,order_id,order_status,fulfill_date,Pro.name,Categories.name,Pro.description,
Pro.image,U.address
FROM Purchases Pur
INNER JOIN Products Pro
ON Pur.pid = Pro.id
INNER JOIN Users U
ON Pur.uid = U.id
INNER JOIN Categories
ON Categories.id = Pro.category
WHERE sid = :sid
AND Pur.id = :oid
ORDER BY time_purchased DESC ,order_id
''',
                              sid=sid,
                              oid=oid)

        return [Purchase(*row) for row in rows]
    def filter_by_conditions(sid,oid,year,status = True):
        rows = app.db.execute('''
SELECT Pur.id, Pur.uid, Pur.pid, Pur.sid, Pur.time_purchased, Pur.quantity,
Pur.price,order_id,order_status,fulfill_date,Pro.name,Categories.name,Pro.description,
Pro.image,U.address
FROM Purchases Pur
INNER JOIN Products Pro
ON Pur.pid = Pro.id
INNER JOIN Users U
ON Pur.uid = U.id
INNER JOIN Categories
ON Categories.id = Pro.category
WHERE sid = :sid
AND Pur.id = :oid and order_status = :status AND time_purchased > year
ORDER BY time_purchased DESC ,order_id
''',
                              sid=sid,
                              oid=oid,
                              status = status,
                              year = year)
