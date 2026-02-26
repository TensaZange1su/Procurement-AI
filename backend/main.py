from fastapi import FastAPI, HTTPException

from backend.sql_builder import (
    extract_enstru,
    extract_year,
    extract_region
)

from backend.analytics import (
    fair_price_analysis,
    volume_analysis,
    price_anomaly_analysis
)

from backend.formatter import (
    format_fairness,
    format_volume,
    format_anomaly
)

app = FastAPI(
    title="Procurement AI",
    version="1.0"
)


@app.post("/query")
def query_ai(payload: dict):

    if "query" not in payload:
        raise HTTPException(400, "query required")

    text = payload["query"]
    text_lower = text.lower()

    enstru = extract_enstru(text)

    if not enstru:
        raise HTTPException(400, "ЕНС ТРУ не найден")

    year = extract_year(text)
    region = extract_region(text)

    # ---------- VOLUME ----------
    if "объем" in text_lower or "объём" in text_lower:

        stats = volume_analysis(enstru)

        return format_volume(text, stats)

    # ---------- FAIR PRICE ----------
    elif "справедлив" in text_lower:

        if not region:
            raise HTTPException(400, "Укажите регион поставки")

        stats = fair_price_analysis(enstru, region, year)

        if not stats:
            raise HTTPException(404, "Недостаточно данных")

        return format_fairness(text, stats)

    # ---------- ANOMALY ----------
    elif "аномал" in text_lower:

        if not region:
            raise HTTPException(400, "Укажите регион поставки")

        stats = price_anomaly_analysis(enstru, region, year)

        if not stats:
            raise HTTPException(404, "Недостаточно данных")

        return format_anomaly(text, stats)

    else:

        raise HTTPException(400, "Тип запроса не распознан")