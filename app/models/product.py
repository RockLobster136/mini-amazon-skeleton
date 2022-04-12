from flask import current_app as app


class Product:
    def __init__(self, id, name, category, description, price, image=None, available=None, creator_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.image = image
        self.available = available
        self.creator_id = creator_id

    # get single product by product id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id,name,category,description,price,image,available,creator_id
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    # get all products (available)
    @staticmethod
    def get_all(available = True):
        rows = app.db.execute('''
SELECT P.id,P.name,C.name,P.description,P.price,P.image,P.available,P.creator_id
FROM Products P, Categories C
WHERE available = :available AND P.category = C.id
ORDER BY P.name
''',
                        available = available )
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
    def add_prod(name,category,description = None, price = None, image = None, available = True, creator_id = None):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category, description, price, image, available)
VALUES(:name, :category, :description, :price, :image, :available)
RETURNING id
""",
                                  name=name,
                                  category=category,
                                  description=description,
                                  price = price,
                                  image=image,
                                  available=available,
                                  creator_id=creator_id)

            id = rows[0][0]
            print("Product added:", id, name, category, description, image, available,creator_id)
            return id
        except Exception as e:
            print(str(e))
            return None

    # update product
    @staticmethod
    def update_prod(name, category, description =None, image = None, available = True, creator_id = None):
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
                                    available=available,
                                    creator_id=creator_id)
            id = rows[0][0]
            print("Product Updated:", id, name, category, description, image, available, creator_id)
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



    