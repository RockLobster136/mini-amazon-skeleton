from flask import current_app as app
from flask_login import login_user, logout_user, current_user
from .user import User
import time

class Cart:
    def __init__(self, product_id, product_name, buyer_id, inventory_id, seller_firstname, seller_lastname, quantity, save_for_later, product_price):
        self.product_id = product_id
        self.product_name = product_name
        self.buyer_id = buyer_id
        self.inventory_id = inventory_id
        self.seller_name = seller_firstname + " " + seller_lastname
        self.quantity = quantity
        self.save_for_later = save_for_later
        self.product_price = product_price
    
    # get cart info for this user
    @staticmethod
    # def user_cart(buyer_id):
    #     rows = app.db.execute(
    #         '''
    #         SELECT P.id AS product_id, P.name AS product_name,C.uid AS buyer_id, C.iid AS inventory_id,  U.firstname AS seller_firstname,
    #             U.lastname AS seller_lastname, C.quantity, C.save_for_later, I.price AS product_price
    #         FROM Carts AS C, Products as P, Inventory as I, Users as U
    #         WHERE C.iid = I.id AND I.pid = P.id AND I.sid = U.id AND C.uid = :uid
    #         ''',
    #         uid = buyer_id
    #     )
    #     return [Cart(*row) for row in rows]
    def user_cart(buyer_id):
        rows = app.db.execute(
            '''
            SELECT P.id AS product_id, P.name AS product_name,C.uid AS buyer_id, C.iid AS inventory_id,  U.firstname AS seller_firstname,
                U.lastname AS seller_lastname, C.quantity, C.save_for_later, I.price AS product_price
            FROM Carts AS C, Products as P, Inventory as I, Users as U
            WHERE C.iid = I.id AND I.pid = P.id AND I.sid = U.id AND C.uid = :uid AND C.save_for_later = FALSE
            ''',
            uid = buyer_id
        )
        return [Cart(*row) for row in rows]
    
    def user_save(buyer_id):
        rows = app.db.execute(
            '''
            SELECT P.id AS product_id, P.name AS product_name,C.uid AS buyer_id, C.iid AS inventory_id,  U.firstname AS seller_firstname,
                U.lastname AS seller_lastname, C.quantity, C.save_for_later, I.price AS product_price
            FROM Carts AS C, Products as P, Inventory as I, Users as U
            WHERE C.iid = I.id AND I.pid = P.id AND I.sid = U.id AND C.uid = :uid AND C.save_for_later = TRUE
            ''',
            uid = buyer_id
        )
        return [Cart(*row) for row in rows]
    
    
    @staticmethod
    def add_to_cart(buyer_id, inventory_id, quantity, product_id):
        rows = app.db.execute(f'''SELECT quantity FROM Carts WHERE iid={inventory_id} AND uid={buyer_id};''')
        if rows is None or len(rows) == 0:
            query = f'''INSERT INTO Carts(id, uid, iid, quantity,save_for_later)
                    VALUES (COALESCE((SELECT MAX(id)+1 FROM Carts),0),{buyer_id}, {inventory_id}, {quantity},FALSE);'''
        else:
            query = f'''UPDATE Carts
                        SET quantity = {int(rows[0][0]) + int(quantity)}
                        WHERE iid={inventory_id} AND uid={buyer_id};'''
        rows = app.db.execute(query)
        return rows
    
    @staticmethod
    def remove_from_cart(buyer_id, inventory_id):
        rows = app.db.execute(f'''DELETE FROM Carts WHERE iid={inventory_id} AND uid={buyer_id};''')
        return rows

    @staticmethod
    def change_quantity(buyer_id, inventory_id, quantity):
        rows = app.db.execute('''UPDATE Carts 
                                 SET quantity = :quantity 
                                 WHERE iid=:inventory_id AND uid=:buyer_id;''',
                              buyer_id=buyer_id, inventory_id=inventory_id, quantity=quantity)
        return rows
    
    @staticmethod
    def update_balance(start,amount,pid,uid,category):
        rows = app.db.execute(
            """INSERT INTO BalanceHistory(start,amount,pid,uid,category)
                VALUES(:start,:amount,:pid,:uid,:category)
                RETURNING id""",
                start = start, amount = amount, pid = pid, uid = uid, category = category
        )
        return rows
        

    @staticmethod
    def place_order(buyer_id):
        rows = app.db.execute(f'''SELECT C.id, P.id, C.iid, C.quantity, I.price, I.sid, I.id, C.save_for_later
                                    FROM Carts AS C, Products AS P, Inventory AS I
                                    WHERE I.pid = P.id
                                    AND C.iid = I.id
                                    AND C.uid = {buyer_id}
                                    AND C.save_for_later = FALSE;''')
        if rows is None or len(rows) == 0:
            return None
        
        # update purchase
        timestamp = int(time.time())
        order_id = int(str(buyer_id) + str(int(time.time())))
        values = [f'({buyer_id},{row[1]},{row[5]},{row[3]},{row[4]},{order_id})' for row in rows]
        purchase_id = app.db.execute(f'''INSERT INTO Purchases (uid,pid,sid,quantity,price,order_id) 
                                    VALUES {",".join(values)} RETURNING id;''')[0][0]

        # update inventory
        queries = [f'''UPDATE Inventory SET quantity = quantity - {row[3]} WHERE id = {row[-2]};''' for row in rows]
        app.db.execute(' '.join(queries))

        # update balance
        amount = sum(row[3]*row[4] for row in rows)
        # update buyer
        ## update BalanceHistory
        Cart.update_balance(current_user.balance, -amount, purchase_id, buyer_id,1)
        ## update user balance？？
        User.mgmt_fund(buyer_id,current_user.balance - amount) 

        # update seller
        for row in rows:
            seller_id = row[5]
            current_seller = User.get(seller_id)
            Cart.update_balance(current_seller.balance, amount, purchase_id, seller_id,2)
            User.mgmt_fund(seller_id,current_seller.balance + amount)

        # delete cart record
        rows = app.db.execute(f'''DELETE FROM Carts WHERE uid={buyer_id} AND save_for_later = FALSE;''')
        return rows
    
    @staticmethod
    def save_for_later(buyer_id, inventory_id):
        rows = app.db.execute('''UPDATE Carts 
                                 SET save_for_later = TRUE 
                                 WHERE iid=:inventory_id AND uid=:buyer_id;''',
                              buyer_id=buyer_id, inventory_id=inventory_id)
        return rows
    
    @staticmethod
    def add_back_to_cart(buyer_id, inventory_id):
        rows = app.db.execute('''UPDATE Carts 
                                 SET save_for_later = FALSE 
                                 WHERE iid=:inventory_id AND uid=:buyer_id;''',
                              buyer_id=buyer_id, inventory_id=inventory_id)
        return rows