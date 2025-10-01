import os, sqlite3, pandas as pd

BASE = os.path.dirname(__file__)
DB   = os.path.join(BASE, "demo.db")
SEED = os.path.join(BASE, "seed")
SQLD = os.path.join(BASE, "sql")
OUT  = os.path.join(BASE, "outputs")

def load_csvs(conn):
    for name in ["customers","products","orders","order_items","shipments","returns"]:
        df = pd.read_csv(os.path.join(SEED, f"{name}.csv"))
        df.to_sql(name, conn, if_exists="append", index=False)
        print(f"Loaded {name}: {len(df):,} rows")

def run_report(conn, name):
    sql_file = os.path.join(SQLD, name + ".sql")
    out_csv  = os.path.join(OUT,  name + ".csv")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()
    df = pd.read_sql_query(sql, conn)
    df.to_csv(out_csv, index=False)
    print(f"✅ {name}.sql  → outputs/{name}.csv  ({len(df)} rows)")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    if os.path.exists(DB): os.remove(DB)
    conn = sqlite3.connect(DB)
    with open(os.path.join(BASE, "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    if not os.path.exists(SEED) or not os.listdir(SEED):
        raise SystemExit("Seed CSVs missing. Run:  python reports/build_seed.py")

    load_csvs(conn)

    # Run your first report
    run_report(conn, "sales_margin_by_region")

    conn.close()
    print("All reports written to reports/outputs/")
