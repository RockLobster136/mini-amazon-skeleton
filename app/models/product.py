from flask import current_app as app


class Product:
    def __init__(self, id, name, category,description, image=None, available=None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.image = image
        self.available = available

    # get single product by product id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, available, category
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    # get all products (available)
    @staticmethod
    def get_all(available = True):
        rows = app.db.execute('''
SELECT id,name,category,description,image,available
FROM Products
WHERE available = :available
ORDER BY name
''',
                        available = available )
        print(rows[0])
        return [Product(*row) for row in rows]
    
    # search product by category
    @staticmethod
    def get_by_category(cat):
        if cat:
            rows = app.db.execute('''
    SELECT P.name
    FROM Products P 
    INNER JOIN Categories C
    ON P.category = C.id
    WHERE C.name = :cat
    ''',cat=cat)
        else:
            return None
        if rows and len(rows) != 0:
            return [row[0] for row in rows]
        return None
    # search product by keyword
    @staticmethod
    def get_by_key(keyword):
        input = "%{}%".format(keyword)
        rows = app.db.execute('''
                                SELECT *
                                FROM Products
                                WHERE LOWER(name) LIKE :keyword OR LOWER(description) LIKE :keyword
                                ''',
                              keyword=input)
        return [Product(*row) for row in rows]

    # add new product
    def add_prod(name,category,description = None, image = None, available = True):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category, description, image, available)
VALUES(:name, :category, :description, :image, :available)
RETURNING id
""",
                                  name=name,
                                  category=category,
                                  description=description,
                                  image=image,
                                  available=available)

            id = rows[0][0]
            print("Product added:", id, name, category, description, image, available)
            return id
        except Exception as e:
            print(str(e))
            return None

    # update product
    @staticmethod
    def update_prod(name, category, description =None, image = None, available = True):
        try:
            rows = app.db.execute("""
    UPDATE Products
    SET name = :name, description = :description, image = :image, price = :price, category = :category
    WHERE creator_id = :creator_id
    """,
                                    name=name,
                                    category=category,
                                    description=description,
                                    image=image,
                                    available=available)
            id = rows[0][0]
            print("Product Updated:", id, name, category, description, image, available)
            return
        except Exception as e:
            print(e)
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
        else:
            return rows[0][0]
    
    def get_prod_cat():
        rows = app.db.execute('''
SELECT *
FROM Categories
''')    
        return [row[1] for row in rows]



    