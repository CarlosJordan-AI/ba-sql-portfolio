-- Drop if re-running
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS returns;

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  region      TEXT NOT NULL,
  segment     TEXT NOT NULL,
  signup_date TEXT NOT NULL
);

CREATE TABLE products (
  sku       TEXT PRIMARY KEY,
  category  TEXT NOT NULL,
  price     REAL NOT NULL,
  cost      REAL NOT NULL
);

CREATE TABLE orders (
  order_id     INTEGER PRIMARY KEY,
  customer_id  INTEGER NOT NULL,
  order_ts     TEXT NOT NULL,
  is_internal  INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  order_id    INTEGER NOT NULL,
  sku         TEXT NOT NULL,
  qty         INTEGER NOT NULL,
  unit_price  REAL NOT NULL,
  unit_cost   REAL NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(order_id),
  FOREIGN KEY(sku)      REFERENCES products(sku)
);

CREATE TABLE shipments (
  order_id     INTEGER PRIMARY KEY,
  carrier      TEXT NOT NULL,
  ship_ts      TEXT NOT NULL,
  delivered_ts TEXT
);

CREATE TABLE returns (
  order_id  INTEGER NOT NULL,
  sku       TEXT NOT NULL,
  qty       INTEGER NOT NULL,
  reason    TEXT NOT NULL,
  return_ts TEXT NOT NULL
);
