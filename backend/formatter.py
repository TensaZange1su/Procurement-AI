def format_fairness(query, stats):

    if not stats:
        return {"error": "Недостаточно данных"}

    verdict = (
        "Цена отклоняется от справедливой"
        if abs(stats["top_k"][0]["fairness_index"] - 1) > 0.3
        else "Цена находится в пределах допустимого отклонения"
    )

    return {
        "1_Краткий_вывод": verdict,
        "2_Использованные_данные": {
            "Запрос": query,
            "N_объектов": stats["n"]
        },
        "3_Сравнение": {
            "Медиана": stats["median"],
            "Среднее": stats["avg"],
            "IQR": stats["iqr"],
            "FairPrice": stats["fair_price"]
        },
        "4_Метрика": "Median + Inflation adjustment",
        "5_Ограничения_и_уверенность": "Региональная выборка, без сезонной корректировки",
        "6_Top_K": stats["top_k"]
    }

def format_volume(query, stats):

    if not stats:
        return {"error": "Недостаточно данных"}

    verdict = (
        "Обнаружено нетипичное изменение объема"
        if stats["anomalies"]
        else "Существенных отклонений объема не выявлено"
    )

    return {
        "1_Краткий_вывод": verdict,
        "2_Использованные_данные": {
            "Запрос": query
        },
        "3_Сравнение": stats["years_data"],
        "4_Метрика": "YoY growth > 30%",
        "5_Ограничения_и_уверенность": "Анализ выполнен на уровне годовой агрегации без сезонной корректировки",
        "6_Top_K": stats["anomalies"]
    }

def format_anomaly(query, stats):

    if not stats:
        return {"error": "Недостаточно данных"}

    verdict = (
        "Обнаружены ценовые аномалии"
        if stats["summary"]["anomaly_count"] > 0
        else "Ценовые аномалии не обнаружены"
    )

    return {
        "1_Краткий_вывод": verdict,

        "2_Использованные_данные": {
            "Запрос": query,
            "Количество_лотов": stats["summary"]["total_lots"]
        },

        "3_Границы_IQR": {
            "Нижняя": stats["summary"]["iqr_lower"],
            "Верхняя": stats["summary"]["iqr_upper"]
        },

        "4_Статистика": {
            "Средняя_цена": stats["summary"]["avg_price"],
            "Минимальная": stats["summary"]["min"],
            "Максимальная": stats["summary"]["max"]
        },

        "5_Аномалии": stats["anomalies"],

        "6_Метод": "IQR + z-score",

        "7_Уверенность": "Высокая"
    }