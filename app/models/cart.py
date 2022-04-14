from flask import current_app as app
from .user import User
import time

class Cart:
    def __init__(self, product_id, product_name, buyer_id, inventory_id, seller_firstname, seller_lastname, quantity, save_for_later, product_price):
        self.product_id = product_id
        self.product_name = product_name
        self.buyer_id = buyer_id
        self.inventory_id = inventory_id
        self.seller = seller_firstname + " " + seller_lastname
        self.quantity = quantity
        self.save_for_later = save_for_later
        self.product_price = product_price
    
    @staticmethod
    def user_cart(buyer_id):
        rows = app.db.execute(
            '''
            SELECT P.id AS product_id, P.name AS product_name,C.uid AS buyer_id, C.iid AS inventory_id,  U.firstname AS seller_firstname,
                U.lastname AS seller_lastname, C.quantity, C.save_for_later, I.price AS product_price
            FROM Carts AS C, Products as P, Inventory as I, Users as U
            WHERE C.iid = I.id AND I.pid = P.id AND I.sid = U.id AND C.uid = :uid
            ''',
            uid = buyer_id
        )
        return [Cart(*rows) for row in rows]
    
    @staticmethod
    def add_to_cart(buyer_id, inventory_id, quantity, product_id):
        rows = app.db.execute(f'''SELECT quantity FROM Carts WHERE inventory_id={inventory_id} AND buyer_id={buyer_id};''')
        if rows is None or len(rows) == 0:
            query = f'''INSERT INTO Carts(id, product_id, buyer_id, inventory_id, quantity,save_for_later)
                    VALUES (COALESCE((SELECT MAX(id)+1 FROM Carts),0), {product_id}, {buyer_id}, {inventory_id}, {quantity},FALSE);'''
        else:
            query = f'''UPDATE Carts
                        SET quantity = {int(rows[0][0]) + int(quantity)}
                        WHERE inventory_id={inventory_id} AND buyer_id={buyer_id};'''
        rows = app.db.execute(query)
        return rows
    
    @staticmethod
    def remove_from_cart(buyer_id, inventory_id):
        rows = app.db.execute(f'''DELETE FROM Carts WHERE inventory_id={inventory_id} AND buyer_id={buyer_id};''')
        return rows

    @staticmethod
    def change_quantity(buyer_id, inventory_id, quantity):
        rows = app.db.execute('''UPDATE Carts 
                                 SET quantity = :quantity 
                                 WHERE inventory_id=:inventory_id AND buyer_id=:buyer_id;''',
                              buyer_id=buyer_id, inventory_id=inventory_id, quantity=quantity)
        return rows
    
    @staticmethod
    def update_balance():

    @staticmethod
    def place_order(buyer_id):
        rows = app.db.execute(f'''SELECT C.id, P.id, C.iid, C.quantity, I.price, I.sid, I.id, C.save_for_later
                                    FROM Carts AS C, Products AS P, Inventory AS I
                                    WHERE I.pid = P.id
                                    AND C.iid = I.id
                                    AND C.uid = {buyer_id};''')
        if rows is None or len(rows) == 0:
            return None
        
        # update purchase
        timestamp = int(time.time())
        order_id = int(str(buyer_id) + str(int(time.time())))
        values = [f'({buyer_id},{row[1]},{row[5]},{row[3]},{row[4]},{order_id})' for row in rows]
        app.db.execute(f'''INSERT INTO Purchases (uid,pid,sid,quantity,price,orderid) 
                                    VALUES {",".join(values)}; RETURNING id;''')

        # update inventory
        queries = [f'''UPDATE Inventory SET quantity = quantity - {row[3]} WHERE id = {row[-2]};''' for row in rows]
        app.db.execute(' '.join(queries))

        ##### update balance??
        ## ->
        #####

        # delete cart record
        rows = app.db.execute(f'''DELETE FROM Carts WHERE buyer_id={buyer_id};''')
        return rows