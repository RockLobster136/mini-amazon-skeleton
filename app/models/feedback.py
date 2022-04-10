from flask import current_app as app
class ProductFeedback:
    def __init__(self, id, uid, pid, product, rating, review, upvotes, time_feedback):
        self.id = id
        self.uid = uid # buyer(reviewer) id
        #self.sid = sid # reviewed seller id
        self.pid = pid # reviewed product id
        self.product = product
        self.rating = rating
        self.review = review
        self.upvotes = upvotes
        self.time_feedback = time_feedback

    @staticmethod
    def get_all_feedbacks(uid):
        # get all feed backs from one reviewer
        rows = app.db.execute('''
        SELECT Products.name AS product, rating, review, time_feedback, upvotes
        FROM ProductFeedback
        JOIN Products
        ON ProductFeedback.pid = Products.id
        WHERE uid = :uid''',
        uid = uid
        )
        if len(rows)>0:
            return [ProductFeedback(*row) for row in rows]
        else:
            return None
    
    @staticmethod
    def add_feedback(id, uid, pid, rating, review, time_feedback, upvotes):
        # insert feedback to ProductFeedback table
        rows = app.db.execute('''
        INSERT INTO ProductFeedback(id, uid, pid, rating, review, time_feedback, upvotes)
        VALUES(:id, :uid, :pid, :rating, :review, :time_feedback, :upvotes)
        ''',
        id = id,
        uic = uid,
        pid = pid,
        rating = rating, 
        review = review, 
        time_feedback = time_feedback, 
        upvotes = upvotes        
        )
        id = rows[0][0]
        return ProductFeedback.get_feedback(id)
    
