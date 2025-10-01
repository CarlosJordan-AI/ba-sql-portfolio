import os
import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)

BASE = os.path.dirname(__file__)
SEED_DIR = os.path.join(BASE, "seed")
os.makedirs(SEED_DIR, exist_ok=True)

def dstr(dt): return dt.strftime("%Y-%m-%d")
def tstr(dt): return dt.strftime("%Y-%m-%d %H:%M:%S")

regions  = ["West","Midwest","South","Northeast"]
segments = ["Consumer","SMB","Enterprise"]
cats     = ["Doors","Frames","Hardware","Accessories"]
carriers = ["UPS","FedEx","Estes","XPO"]
reasons  = ["Damaged","Wrong item","Buyer remorse"]

today = datetime(2025, 9, 1)
start = today - timedelta(days=365)

# -----------------------
# Customers
# -----------------------
cust = []
for cid in range(1, 801):
    signup = start + timedelta(days=random.randint(0, 330))
    cust.append(dict(
        customer_id=cid,
        region=random.choice(regions),
        segment=random.choices(segments, weights=[6,3,1])[0],
        signup_date=dstr(signup)
    ))
pd.DataFrame(cust).to_csv(os.path.join(SEED_DIR, "customers.csv"), index=False)

# -----------------------
# Products
# -----------------------
prod = []
for i in range(1, 151):
    cat = random.choices(cats, weights=[4,3,2,1])[0]
    sku = f"SKU{i:04d}"
    base = {"Doors":400, "Frames":250, "Hardware":60, "Accessories":25}[cat]
    price = round(random.uniform(base*0.9, base*1.2), 2)
    cost  = round(price * random.uniform(0.55, 0.8), 2)
    prod.append(dict(sku=sku, category=cat, price=price, cost=cost))
pd.DataFrame(prod).to_csv(os.path.join(SEED_DIR, "products.csv"), index=False)

# -----------------------
# Orders & Items
# -----------------------
orders, items = [], []
oid = 1
for _ in range(2200):
    cid = random.randint(1, 800)
    days_back = max(0, int(abs(random.gauss(110, 85))))
    otime = max(start, today - timedelta(days=days_back))
    is_internal = 1 if random.random() < 0.03 else 0

    orders.append(dict(
        order_id=oid,
        customer_id=cid,
        order_ts=tstr(otime),
        is_internal=is_internal
    ))

    # 1–4 lines per order
    for _ in range(random.randint(1, 4)):
        sku_row = random.randint(1, 150)
        qty = random.randint(1, 4)
        # No placeholders for price/cost here
        items.append(dict(order_id=oid, sku=f"SKU{sku_row:04d}", qty=qty))

    oid += 1

orders_df = pd.DataFrame(orders)
items_df  = pd.DataFrame(items)

# Bring in price/cost from products
prods = pd.read_csv(os.path.join(SEED_DIR, "products.csv"))
items_df = items_df.merge(prods[["sku", "price", "cost"]], on="sku", how="left")
items_df.rename(columns={"price": "unit_price", "cost": "unit_cost"}, inplace=True)

# ✅ DEFENSIVE: if duplicates slipped in, take the LAST column matching the name
# (This handles cases where a prior run or a merge created duplicate headers.)
unit_price_series = items_df.filter(regex=r'^unit_price(\.\d+)?$').iloc[:, -1]
unit_cost_series  = items_df.filter(regex=r'^unit_cost(\.\d+)?$').iloc[:, -1]

# Rebuild the exact schema order & single header set
items_df = pd.DataFrame({
    "order_id":  items_df["order_id"].astype(int),
    "sku":       items_df["sku"],
    "qty":       items_df["qty"].astype(int),
    "unit_price":unit_price_series.astype(float),
    "unit_cost": unit_cost_series.astype(float),
})

# (Optional sanity check)
print("order_items columns (final):", list(items_df.columns))

orders_df.to_csv(os.path.join(SEED_DIR, "orders.csv"), index=False)
items_df.to_csv(os.path.join(SEED_DIR, "order_items.csv"), index=False)

# -----------------------
# Shipments
# -----------------------
ship = []
for _, o in orders_df.iterrows():
    ship_offset = random.randint(0, 3)
    ship_ts = datetime.strptime(o.order_ts, "%Y-%m-%d %H:%M:%S") + timedelta(days=ship_offset)
    in_transit = random.random() < 0.05
    delivered = None if in_transit else ship_ts + timedelta(days=random.randint(1, 7))
    ship.append(dict(
        order_id=int(o.order_id),
        carrier=random.choice(carriers),
        ship_ts=tstr(ship_ts),
        delivered_ts=None if in_transit else tstr(delivered)
    ))
pd.DataFrame(ship).to_csv(os.path.join(SEED_DIR, "shipments.csv"), index=False)

# -----------------------
# Returns (~8% of orders)
# -----------------------
rets, chosen = [], set()
for _ in range(int(len(orders_df) * 0.08)):
    o = orders_df.sample(1, random_state=random.randint(0, 100)).iloc[0]
    if o.order_id in chosen:
        continue
    chosen.add(o.order_id)

    oi = items_df[items_df.order_id == o.order_id].sample(
        1, random_state=random.randint(0, 100)
    ).iloc[0]
    qty = max(1, int(round(oi.qty * random.uniform(0.2, 0.8))))
    rts = datetime.strptime(o.order_ts, "%Y-%m-%d %H:%M:%S") + timedelta(days=random.randint(2, 30))
    rets.append(dict(
        order_id=int(o.order_id),
        sku=oi.sku,
        qty=qty,
        reason=random.choice(reasons),
        return_ts=dstr(rts)
    ))
pd.DataFrame(rets).to_csv(os.path.join(SEED_DIR, "returns.csv"), index=False)

print("✅ Seed CSVs written to reports/seed")
