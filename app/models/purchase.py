from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, sid, time_purchased, quantity, price):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.time_purchased = time_purchased
        self.quantity = quantity
        self.price = price

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
SELECT id, uid, pid, sid, time_purchased, quantity, price
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
