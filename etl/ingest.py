import os
import requests
import psycopg2
from psycopg2.extras import execute_values
import json
import time
import random

BASE_URL = "https://ows.goszakup.gov.kz/v3/lots"
TOKEN = os.getenv("PGZ_TOKEN")

# ---------------- CONFIG ----------------

DB_PARAMS = dict(
    dbname="procurement",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

BINS = [
'000740001307','020240002363','020440003656','030440003698',
'050740004819','051040005150','100140011059','120940001946',
'140340016539','150540000186','171041003124','210240019348',
'210240033968','210941010761','230740013340','231040023028',
'780140000023','900640000128','940740000911','940940000384',
'960440000220','970940001378','971040001050','980440001034',
'981140001551','990340005977','990740002243'
]

LIMIT_PER_REQUEST = 200
MAX_RECORDS_PER_BIN = 100000


# ---------------- SESSION FACTORY ----------------

def create_session():

    s = requests.Session()

    s.headers.update({
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": f"Mozilla/5.0 random-{random.randint(1000,9999)}",
        "Accept": "application/json",
        "Connection": "keep-alive"
    })

    return s


session = create_session()


# ---------------- SAVE FUNCTION ----------------

def save_raw(items, cur):

    if not items:
        return 0

    records = [
        (item["id"], json.dumps(item))
        for item in items
    ]

    execute_values(
        cur,
        """
        INSERT INTO raw_lots (source_id, json_data)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        records
    )
    return cur.rowcount

# ---------------- FETCH FUNCTION ----------------

def fetch_lots_by_bin(bin_value):

    session = create_session()

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print(f"\nLoading BIN {bin_value}")

    search_after = None
    total_inserted = 0
    page = 0
    retry = 0

    while True:

        params = {
            "limit": LIMIT_PER_REQUEST,
            "system_id": 3,
            "customer_bin": bin_value,
            "index_date_from": "2023-01-01",
            "index_date_to": "2026-12-31"
        }

        if search_after:
            params["search_after"] = search_after

        try:

            r = session.get(BASE_URL, params=params, timeout=30)

        except Exception:

            time.sleep(5)
            session = create_session()
            continue

        if r.status_code == 200:

            retry = 0

            data = r.json()
            items = data.get("items", [])

            if not items:
                break

            inserted = save_raw(items, cur)

            conn.commit()

            total_inserted += inserted
            page += 1

            print(
                f"BIN {bin_value} page {page} inserted {inserted} total {total_inserted}"
            )

            next_page = data.get("next_page")

            if not next_page:
                break

            search_after = next_page.split("search_after=")[-1]

            time.sleep(random.uniform(0.02, 0.08))

        elif r.status_code == 403:

            retry += 1
            wait = min(60, retry * 5)

            print(f"403 blocked, wait {wait}s")

            time.sleep(wait)
            session = create_session()

        else:

            print("ERROR", r.status_code)
            time.sleep(5)
            session = create_session()

    cur.close()
    conn.close()

    print(f"BIN COMPLETE {bin_value} inserted {total_inserted}")

    return total_inserted

# ---------------- RUN FUNCTION ----------------
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 4
def run_archive():

    grand_total = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(fetch_lots_by_bin, bin_value): bin_value
            for bin_value in BINS
        }

        for future in as_completed(futures):

            bin_value = futures[future]

            try:
                inserted = future.result()
                grand_total += inserted

                print(f"BIN DONE {bin_value}, inserted {inserted}")
                print(f"GRAND TOTAL: {grand_total}")

            except Exception as e:

                print(f"BIN FAILED {bin_value}: {e}")

    print("ALL DONE")


# ---------------- MAIN ----------------

if __name__ == "__main__":

    if not TOKEN:
        print("ERROR: PGZ_TOKEN not set")
        exit(1)

    run_archive()