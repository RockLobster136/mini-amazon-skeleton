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
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
