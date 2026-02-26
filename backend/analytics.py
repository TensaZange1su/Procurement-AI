from clickhouse_driver import Client
import statistics

# ---------- SINGLETON CLIENT ----------

ch = Client(
    host="localhost",
    port=9000,
    user="app",
    password="admin",
    database="procurement",
    send_receive_timeout=30
)


# ---------- FAIR PRICE ----------

def fair_price_analysis(enstru_code, region=None, year=None):

    query = """
        SELECT
            avg(unit_price),
            quantile(0.25)(unit_price),
            quantile(0.75)(unit_price),
            count()
        FROM procurement.fact_lots
        WHERE enstru_code = %(enstru)s
    """

    params = {"enstru": enstru_code}

    if region:
        query += " AND region = %(region)s"
        params["region"] = region

    if year:
        query += " AND year = %(year)s"
        params["year"] = year

    result = ch.execute(query, params)

    if not result or result[0][3] == 0:
        return None

    avg_price, q1, q3, total = result[0]

    return {
        "avg_price": float(avg_price),
        "q1": float(q1),
        "q3": float(q3),
        "total": int(total)
    }


# ---------- VOLUME ----------

def volume_analysis(enstru_code):

    query = """
    SELECT
        year,
        sum(quantity)
    FROM fact_lots
    WHERE enstru_code = %(enstru)s
    GROUP BY year
    ORDER BY year
    """

    result = ch.execute(query, {"enstru": enstru_code})

    if not result:
        return None

    years_data = []
    anomalies = []

    prev = None

    for year, volume in result:

        years_data.append({
            "year": year,
            "volume": float(volume)
        })

        if prev:
            growth = (volume - prev) / prev

            if abs(growth) > 0.3:
                anomalies.append({
                    "year": year,
                    "growth": growth
                })

        prev = volume

    return {
        "years_data": years_data,
        "anomalies": anomalies
    }


# ---------- PRICE ANOMALY (PRODUCTION) ----------

def price_anomaly_analysis(enstru_code, region, year=None):

    query = """
    SELECT
        lot_id,
        unit_price
    FROM fact_lots
    WHERE enstru_code = %(enstru)s
      AND region = %(region)s
    """

    params = {
        "enstru": enstru_code,
        "region": region
    }

    if year:
        query += " AND year = %(year)s"
        params["year"] = year

    result = ch.execute(query, params)

    if len(result) < 10:
        return None

    prices = [row[1] for row in result]

    mean = statistics.mean(prices)
    std = statistics.stdev(prices)

    anomalies = []

    for lot_id, price in result:

        z = (price - mean) / std if std > 0 else 0

        if abs(z) > 3:
            anomalies.append({
                "lot_id": lot_id,
                "price": price,
                "z_score": z
            })

    return {
        "mean": mean,
        "std": std,
        "anomalies": anomalies[:20]
    }