-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    isseller BOOLEAN NOT NULL,
    balance DECIMAL(12,2) NOT NULL
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, -- mac
    -- uid INT NOT NULL REFERENCES Users(id), -- seller id
    name VARCHAR(255) UNIQUE NOT NULL,
    -- price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    category INT NOT NULL -- laptop
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id), -- buyer id
    pid INT NOT NULL, -- get product, copied from invetory
    sid INT NOT NULL, -- get seller, copied from inventory
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
    quantity INT NOT NULL CHECK (quantity >= 0), -- quant ordered
    price DECIMAL(12,2) NOT NULL -- price sold/bought
);

-- purchase THEN order
CREATE TABLE Order(
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    pur_id INT NOT NULL REFERENCES Purchases(id), -- get seller, quant, price
    status BOOLEAN DEFAULT FALSE, -- item fulfillment
    order INT NOT NULL, -- batch id, generated from uid + time_stamp
    order_status BOOLEAN DEFAULT FALSE -- batch fulfillment
);

CREATE TABLE Inventory(
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    sid INT NOT NULL REFERENCES Users(id), -- seller id
    pid INT NOT NULL REFERENCES Products(id), -- product name, category
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(12,2) NOT NULL, -- specific to seller, up-to-date
    release_date timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE Cart(
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id), -- buyer id
    iid INT NOT NULL REFERENCES Inventory(id), -- get price, quantity, seller
    time_added timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    quantity INT NOT NULL CHECK (quantity >= 0) -- buyer's quantity
);

CREATE TABLE Rating(
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    sid INT NOT NULL REFERENCES Users(id), -- seller id
    pid INT NOT NULL REFERENCES Products(id), -- product name, category
    rating INT,
    review TEXT
)
