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
    @staticmethod
    def add_prod(name,category,description = None, price = None, image = None, available = True, creator_id = None):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category, description, price, image, available, creator_id)
VALUES(:name, :category, :description, :price, :image, :available,:creator_id)
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
    @staticmethod
    def delete_prod(pid):
        rows = app.db.execute("""
DELETE FROM Inventory
WHERE pid = :pid
RETURNING id
""",
                              pid = pid)
        rows = app.db.execute("""
DELETE FROM Products
WHERE id = :pid
RETURNING id
""",
                              pid = pid)
        if len(rows) != 0:
            return rows[0][0]
        else:
            return None
    # update product
    @staticmethod
    def update_prod(pid,name, description =None, image = None):
        try:
            rows = app.db.execute("""
    UPDATE Products
    SET name = :name, description = :description, image = :image
    WHERE id = :pid
    """,                            pid = pid,
                                    name=name,
                                    description=description,
                                    image=image,
                                    )
            return rows
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
    def search_prod(prod_name, sort_by, des, cat, price_l, price_h, rating_l, rating_h, avail):
        p_name = prod_name.strip(" ")
        p_name_match = f"""'%{p_name[0]}%"""
        if len(p_name) > 2:
            for i in range(1,len(p_name)-1):
                p_name_match = p_name_match + f"""%{p_name[i]}%"""
        p_name_match = p_name_match + f"""%{p_name[len(p_name)-1]}%'"""
        if cat != "All":
            cate = f"""'{cat}'"""
            cate_switch = f""" """
        else:
            cate = f""" """
            cate_switch = f"""--"""
        if sort_by == "price":
            product_sort = f"""ac.min_price"""
        else:
            product_sort = f"""ac.cnt DESC"""
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
            des_match = f""" """
        rows = app.db.execute(f"""
WITH
ratings(pid, rating) as
(SELECT pid, round(avg(rating),2)
FROM ProductFeedback
GROUP BY pid),
cat_temp(id, name) as
(SELECT id, name
FROM Categories
{cate_switch} WHERE name = {cate}
),
avail_cnt(pid, min_price, cnt) as
(SELECT pid, min(price),count(*)
FROM Inventory
GROUP BY pid)

SELECT pro.id as id, ca.name as ca_name, pro.name as name, ac.min_price as price, ac.cnt as avail, r.rating as rating, pro.description as des, pro.image as img
FROM Products pro JOIN avail_cnt ac ON pro.id = ac.pid JOIN ratings r ON r.pid = pro.id JOIN cat_temp ca ON ca.id = pro.category
WHERE
LOWER(pro.name) LIKE {p_name_match}
AND ac.min_price >= :price_l
AND ac.min_price <= :price_h
AND r.rating >= :rating_l
AND r.rating <= :rating_h
AND ac.cnt >= :avail
{switch_des} AND LOWER(pro.description) LIKE {des_match}
{cate_switch} AND pro.category = ca.id
ORDER BY {product_sort}, pro.name""",
            price_l = price_l,
            price_h = price_h,
            rating_l = rating_l,
            rating_h = rating_h,
            avail = avail)
        return rows

    @staticmethod
    def get_own_prod(sid):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE creator_id = :sid
''',
                              sid=sid)

        return [Product(*row) for row in rows]
