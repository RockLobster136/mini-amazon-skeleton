from flask import current_app as app
from .product import Product

# product feedback

class ProductFeedback:
    def __init__(self, id, uid, pid, product_name, rating, review, upvotes, time_feedback):
        self.id = id
        self.uid = uid # buyer(reviewer) id
        self.pid = pid # reviewed product id
        self.product_name = product_name
        self.rating = rating
        self.review = review
        self.upvotes = upvotes
        self.time_feedback = time_feedback

    @staticmethod
    def get_all_feedbacks(uid):
        # get all feed backs from one reviewer
        rows = app.db.execute('''
        SELECT ProductFeedback.id AS id, uid, ProductFeedback.pid AS pid, Products.name AS product_name, rating, review, upvotes, time_feedback
        FROM ProductFeedback
        JOIN Products
        ON ProductFeedback.pid = Products.id
        WHERE uid = :uid
        ORDER BY time_feedback DESC
        ''',
        uid = uid
        )
        if len(rows)>0:
            return [ProductFeedback(*row) for row in rows]
        else:
            return None
    
    @staticmethod
    def add_feedback(uid, pid, rating, review):
        # insert feedback to ProductFeedback table
        rows = app.db.execute('''
        INSERT INTO ProductFeedback(uid, pid, rating, review, upvotes)
        VALUES(:uid, :pid, :rating, :review, 0)
        RETURNING id
        ''',
        uid = uid,
        pid = pid,
        rating = rating, 
        review = review
        )
        id = rows[0][0]
        print(id)
        return id
    
    @staticmethod
    def non_reviewed_products(uid):
        # return non_reviewed products from a buyer
        rows = app.db.execute('''
        SELECT name
        FROM
        (SELECT t1.pid AS pid
        FROM 
        (Select Distinct pid FROM Purchases WHERE uid = :uid) AS t1
        LEFT JOIN
        (Select Distinct pid FROM ProductFeedback WHERE uid = :uid) AS t2
        ON t1.pid = t2.pid
        WHERE t2.pid IS NULL) AS t3
        INNER JOIN Products
        ON t3.pid = Products.id
        ''',
        uid = uid,      
        )
        return [product[0] for product in rows]

    @staticmethod
    def update_product_review(id, rating, review, delete=False):
        if delete:
            rows = app.db.execute('''
        DELETE FROM ProductFeedback
        WHERE id = :id
        RETURNING id
        ''',id = id)
            if len(rows)>0:
                return rows[0][0]
            else:
                return None
        else:
            rows = app.db.execute('''
            UPDATE ProductFeedback
            SET rating = :rating, review =:review
            WHERE id = :id
            RETURNING id
            ''',
            id = id, rating = rating, review = review)
            if len(rows)>0:
                return rows[0][0]
            else:
                return None

    @staticmethod
    def summary_rating(available = True):
        rows = app.db.execute('''
        SELECT Products.id,Products.name,Categories.name AS category,description,price,image,available,creator_id,        
        CASE WHEN cnt_rating IS NULL THEN 0 ELSE cnt_rating END AS cnt_rating, avg_rating
        FROM
        Products 
        Left JOIN
        (
            SELECT ROUND(AVG(rating),2) AS avg_rating, COUNT(rating) AS cnt_rating, pid
            FROM ProductFeedback
            GROUP BY pid
        ) AS t1
        ON Products.id = t1.pid
        INNER JOIN Categories
        ON Products.category = Categories.id
        WHERE Products.available = :available
        ORDER BY Products.name
        ''', available = available)
        return [Product(*row) for row in rows]

    @staticmethod
    def upvote_product_review(id, update):
        '''
        id: feedback id
        update: change of num of upvotes
        '''
        rows = app.db.execute('''
        UPDATE ProductFeedback
        SET upvotes = upvotes + :update
        WHERE id = :id
        RETURNING id
        ''',
        id = id, update = update)
        if len(rows)>0:
            return rows[0][0]
        else:
            return None

# new
    @staticmethod
    def check_purchase_product(uid, pid):
        rows = app.db.execute('''
        SELECT id
        FROM Purchases
        WHERE uid = :uid AND pid = :pid
        ''', 
        uid = uid,
        pid = pid)
        if len(rows)>0:
            return True
        else:
            return False

    @staticmethod
    def find_product_feedbackid(uid, pid):
        rows = app.db.execute('''
        SELECT id
        FROM ProductFeedback
        WHERE uid = :uid AND pid = :pid
        ''', 
        uid = uid,
        pid = pid)
        if len(rows)>0:
            return rows[0][0]
        else:
            return None

# seller feedback

class SellerFeedback:
    def __init__(self, id, uid, sid, seller_name, rating, review, upvotes, time_feedback):
        self.id = id
        self.uid = uid # buyer(reviewer) id
        self.sid = sid # reviewed seller id
        self.seller_name = seller_name
        self.rating = rating
        self.review = review
        self.upvotes = upvotes
        self.time_feedback = time_feedback

    @staticmethod
    def get_all_feedbacks(uid):
        # get all feed backs from one reviewer
        rows = app.db.execute('''
        SELECT SellerFeedback.id AS id, uid, SellerFeedback.sid AS sid, 
        CONCAT(Users.firstname, ' ', Users.lastname) AS seller_name, rating, review, upvotes, time_feedback
        FROM SellerFeedback
        JOIN Users
        ON SellerFeedback.sid = Users.id
        WHERE uid = :uid
        ORDER BY time_feedback DESC
        ''',
        uid = uid
        )
        if len(rows)>0:
            return [SellerFeedback(*row) for row in rows]
        else:
            return None
    
    @staticmethod
    def add_feedback(uid, sid, rating, review):
        # insert feedback to SellerFeedback table
        rows = app.db.execute('''
        INSERT INTO SellerFeedback(uid, sid, rating, review, upvotes)
        VALUES(:uid, :sid, :rating, :review, 0)
        RETURNING id
        ''',
        uid = uid,
        sid = sid,
        rating = rating, 
        review = review
        )
        id = rows[0][0]
        print(id)
        return id
    
    @staticmethod
    def non_reviewed_sellers(uid):
        # return non_reviewed sellers from a buyer
        rows = app.db.execute('''
        SELECT t1.sid AS sid
        FROM 
        (Select Distinct sid FROM Purchases WHERE uid = :uid) AS t1
        LEFT JOIN
        (Select Distinct sid FROM SellerFeedback WHERE uid = :uid) AS t2
        ON t1.sid = t2.sid
        WHERE t2.sid IS NULL
        ''',
        uid = uid,      
        )
        return [sid[0] for sid in rows]

    @staticmethod
    def update_seller_review(id, rating, review, delete=False):
        if delete:
            rows = app.db.execute('''
        DELETE FROM SellerFeedback
        WHERE id = :id
        RETURNING id
        ''',id = id)
            if len(rows)>0:
                return rows[0][0]
            else:
                return None
        else:
            rows = app.db.execute('''
            UPDATE SellerFeedback
            SET rating = :rating, review = :review
            WHERE id = :id
            RETURNING id
            ''',
            id = id, rating = rating, review = review)
            if len(rows)>0:
                return rows[0][0]
            else:
                return None

    @staticmethod
    def upvote_seller_review(id, update):
        '''
        id: feedback id
        update: change of num of upvotes
        '''
        rows = app.db.execute('''
        UPDATE SellerFeedback
        SET upvotes = upvotes + :update
        WHERE id = :id
        RETURNING id
        ''',
        id = id, update = update)
        if len(rows)>0:
            return rows[0][0]
        else:
            return None

    @staticmethod
    def seller_feedback_summary(sid):
        rows = app.db.execute('''
        SELECT avg_rating, rank
        (SELECT sid, avg_rating, RANK() OVER (ORDER BY avg_rating) AS rank
        FROM (SELECT sid, AVG(rating) AS avg_rating
        FROM SellerFeedback
        GROUP BY sid) AS t1) AS t2
        WHERE sid = :sid
        ''', 
        sid = sid
        )
        if len(rows)>0:
            return rows[0]
        else:
            return [-1,-1] # return -1 when no feedback

# new
    @staticmethod
    def check_purchase_seller(uid, sid):
        rows = app.db.execute('''
        SELECT id
        FROM Purchases
        WHERE uid = :uid AND sid = :sid
        ''', 
        uid = uid,
        sid = sid)
        if len(rows)>0:
            return True
        else:
            return False


    @staticmethod
    def find_seller_feedbackid(uid, sid):
        rows = app.db.execute('''
        SELECT id
        FROM SellerFeedback
        WHERE uid = :uid AND sid = :sid
        ''', 
        uid = uid,
        sid = sid)
        if len(rows)>0:
            return rows[0][0]
        else:
            return None