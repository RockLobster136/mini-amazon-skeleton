from flask import current_app as app

class Category:
    def __init__(self,name):
        self.name = name

    # get all avaliable categories in the database
    @staticmethod
    def get_by_id(cid:int):
        rows = app.db.execute(f'''
                SELECT id AS cid, name AS name
                FROM Categories
                WHERE id = {cid}
            ''')
        return Categories(*(rows[0])) if rows is not None else None
