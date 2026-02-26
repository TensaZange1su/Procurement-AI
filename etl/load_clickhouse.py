from clickhouse_driver import Client
import psycopg2
from datetime import date

BATCH_SIZE = 10000

pg = psycopg2.connect(
    dbname="procurement",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

ch = Client(
    host="localhost",
    port=9000,
    user="app",
    password="admin",
    database="procurement"
)

cur = pg.cursor(name="pg_cursor")

cur.execute("""
SELECT
    lot_id,
    customer_bin,
    supplier_bin,
    enstru_code,
    region,
    quantity,
    unit_price,
    total_price,
    publish_date,
    year
FROM fact_lots_cleaned
""")

total_loaded = 0

while True:

    rows = cur.fetchmany(BATCH_SIZE)

    if not rows:
        break

    clean_rows = []

    for row in rows:

        publish_date = row[8] if isinstance(row[8], date) else date(1970,1,1)

        clean_rows.append((
            row[0],
            row[1] or "",
            row[2] or "",
            row[3] or "",
            row[4] or "",
            float(row[5] or 0),
            float(row[6] or 0),
            float(row[7] or 0),
            publish_date,
            int(row[9] or 0)
        ))

    ch.execute(
        "INSERT INTO fact_lots VALUES",
        clean_rows
    )

    total_loaded += len(clean_rows)

    print(f"Loaded: {total_loaded}")

print("DONE")