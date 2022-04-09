from flask import current_app as app


class Product:
    def __init__(self, id, name, available, category):
        self.id = id
        self.name = name
        self.available = available
        self.category = category

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available = True):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE available =: available
''',
                            available = available)
        return [Product(*row) for row in rows]
    
    
    # add new kind of product
    def add_prod(name,category):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category)
VALUES(:name, :category)
RETURNING id
""",
                                  name=name,
                                  category=category)

            id = rows[0][0]
            return id
        except Exception as e:
            print(str(e))
            return None

    # check if prod name exist
    def prod_exist(name):
        rows = app.db.execute('''
SELECT id
FROM Products
WHERE name = :name
''',
                              name=name)
        return len(rows) > 0
    
    
    # find pid for product name
    def prod_find(name):
        rows = app.db.execute('''
SELECT id
FROM Products
WHERE name = :name
''',
                              name=name)
        if len(rows) == 0:
            return None
        return rows[0][0]

    