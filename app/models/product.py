from flask import current_app as app


class Product:
    def __init__(self, id, name, category, description, price, image=None, available=None, creator_id=None, cnt_rating = -1, avg_rating = -1):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.image = image
        self.available = available
        self.creator_id = creator_id
        self.cnt_rating = cnt_rating
        self.avg_rating = avg_rating

    # get single product by product id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Products.id,Products.name,Categories.name,description,price,image,available,creator_id
FROM Products
INNER JOIN Categories
ON Products.category = Categories.id
WHERE Products.id = :id
''',
                              id=id)
        if rows:
            return Product(*(rows[0])) 
        else: return None

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
    @staticmethod
    def search_prod(prod_name, sort_by, sell_fn, sell_ln, des, cat, price_l, price_h, rating_l, rating_h, avail):
        product_n = f"""'%{prod_name}%'"""
        if cat != "All":
            cate = f"""{cat}"""
            cate_switch = f""" """
        else:
            cate = f""" """
            cate_switch = f"""--"""
        if sort_by == "price":
            product_sort = f"""{sort_by}"""
        else:
            product_sort = f"""{sort_by} DESC"""
        product_des = f"""'%{des}%'"""
        if des != "optional":
            switch_des = " "
            des_words = des.strip(" ")
            des_match = f"""'%{des_words[0]}%"""
            if len(des_words) > 2:
                for i in range(1,len(des_words)-1):
                    des_match = des_match + f"""%{des_words[i]}%"""
            des_match = des_match + f"""%{des_words[len(des_words) - 1]}%'"""
        else:
            switch_des = f"""--"""
        if (sell_fn != "optional" and sell_ln == "optional") or (sell_fn == "optional" and sell_ln != "optional"):
            if sell_fn == "optional" and sell_ln != "optional":
                name_field = f"""lastname"""
                temp = f"""{sell_ln}"""
            if sell_fn != "optional" and sell_ln == "optional":
                name_field = f"""firstname"""
                temp = f"""{sell_fn}"""
            rows = app.db.execute(f"""
WITH
inv_users(pid, price, quantity, f_na, l_na) as
(SELECT pid, price, quantity, U.firstname as f_na, U.lastname as l_na
FROM Inventory I JOIN Users U ON I.sid = U.id),
ratings(pid, rating) as
(SELECT pid, rating
FROM ProductFeedback)
cat_temp(id, name) as
(SELECT id, name
FROM Categories
{cate_switch} WHERE name = {cate})

SELECT pro.id as id, ca.name as ca_name, pro.name as name, iu.price and pirce, iu.quantity as avail,
iu.firstname as firstname, iu.lastname as lastname, r.rating as rating, pro.description as des, pro.image as img
FROM Products pro JOIN inv_users iu ON pro.id = iu.pid JOIN ratings r ON r.pid = pro.id JOIN cat_temp ca ON ca.id = pro.category
WHERE LOWER(pro.name) LIKE {product_n}
AND LOWER({name_field}) LIKE {temp}
{switch_des} AND LOWER(pro.description) LIKE {des_match}
{cate_switch} AND pro.category = {cate}
AND inv.price >= :price_l
AND inv.price <= :price_h
AND r.rating >= :rating_l
AND r.rating <= :rating_h
GROUP BY pro.id
HAVING iu.quantity >= :avail
ORDER BY {product_sort}, id""",
            price_l = price_l,
            price_h = price_h,
            rating_l = rating_l,
            rating_h = rating_h,
            avail = avail)
            return rows

        if firstname != "optional" and lastname != "optional":
            temp_fn = f"""'%{sell_fn}%'"""
            temp_ln = f"""'%{sell_ln}%'"""
            rows = app.db.execute(f"""
WITH
inv_users(pid, price, quantity, f_na, l_na) as
(SELECT pid, price, quantity, U.firstname as f_na, U.lastname as l_na
FROM Inventory I JOIN Users U ON I.sid = U.id),
ratings(pid, rating) as
(SELECT pid, rating
FROM ProductFeedback)
cat_temp(id, name) as
(SELECT id, name
FROM Categories
{cate_switch} WHERE name = {cate})

SELECT pro.id as id, pro.name as name, iu.price and pirce, iu.quantity as avail,
iu.firstname as firstname, iu.lastname as lastname, r.rating as rating, pro.description as des, pro.image as img
FROM Products pro JOIN inv_users iu ON pro.id = iu.pid JOIN ratings r ON r.pid = pro.id
WHERE LOWER(pro.name) LIKE {product_n}
AND LOWER(iu.firstname) LIKE {temp_fn}
AND LOWER(iu.lastname) LIKE {temp_ln}
{switch_des} AND LOWER(pro.description) LIKE {des_match}
{cate_switch} AND pro.category = {cate}
AND inv.price >= :price_l
AND inv.price <= :price_h
AND r.rating >= :rating_l
AND r.rating <= :rating_h
GROUP BY pro.id
HAVING iu.quantity >= :avail
ORDER BY {product_sort}, id""",
            price_l = price_l,
            price_h = price_h,
            rating_l = rating_l,
            rating_h = rating_h,
            avail = avail)
            return rows
        return None
