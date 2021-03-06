\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.inventory_id_seq',
                         (SELECT MAX(id)+1 FROM Inventory),
                         false);

\COPY ProductFeedback FROM 'ProductFeedback.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.productfeedback_id_seq',
                         (SELECT MAX(id)+1 FROM ProductFeedback),
                         false);

\COPY SellerFeedback FROM 'SellerFeedback.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.sellerfeedback_id_seq',
                         (SELECT MAX(id)+1 FROM SellerFeedback),
                         false);