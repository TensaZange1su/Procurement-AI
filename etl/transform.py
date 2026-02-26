import psycopg2
from psycopg2.extras import execute_values

DB_PARAMS = dict(
    dbname="procurement",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

BATCH_SIZE = 5000


def run():

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print("Truncating fact_lots_cleaned...")
    cur.execute("TRUNCATE fact_lots_cleaned")

    print("Loading raw_lots...")
    cur.execute("SELECT json_data FROM raw_lots")
    rows = cur.fetchall()

    buffer = []
    inserted = 0

    for (raw,) in rows:

        quantity = float(raw.get("count") or 0)
        total_price = float(raw.get("amount") or 0)

        if quantity <= 0 or total_price <= 0:
            continue

        unit_price = total_price / quantity

        publish_date = raw.get("index_date")

        if not publish_date:
            continue

        year = int(publish_date[:4])

        enstru_list = raw.get("enstru_list") or []
        enstru_code = str(enstru_list[0]) if enstru_list else "0"

        region_list = raw.get("pln_point_kato_list") or []
        region = region_list[0] if region_list else ""

        buffer.append((
            raw["id"],
            raw.get("customer_bin") or "",
            "",  # supplier_bin пока нет
            enstru_code,
            region,
            quantity,
            unit_price,
            total_price,
            publish_date[:10],
            year
        ))

        if len(buffer) >= BATCH_SIZE:

            execute_values(
                cur,
                """
                INSERT INTO fact_lots_cleaned
                VALUES %s
                """,
                buffer
            )

            inserted += len(buffer)
            print(f"Inserted {inserted}")

            buffer.clear()

    # вставка остатка
    if buffer:
        execute_values(
            cur,
            "INSERT INTO fact_lots_cleaned VALUES %s",
            buffer
        )

        inserted += len(buffer)

    conn.commit()

    cur.close()
    conn.close()

    print(f"\nDone. Total inserted: {inserted}")


if __name__ == "__main__":
    run()