import requests
from backend.analytics import price_anomaly_analysis

BASE_URL = "http://localhost:8000/query"

TEST_CASES = [
    {"query": "Найди аномалии по 301000000 2025"},
    {"query": "Найди аномалии по 123456789 2024"},
    {"query": "Найди аномалии по 441234567 2026"}
]

def compare_numbers(api_response, sql_stats):
    matches = 0
    total = 3

    if abs(api_response["3_Сравнение"]["Средневзвешенная"] - sql_stats["weighted_avg"]) < 0.01:
        matches += 1

    if abs(api_response["3_Сравнение"]["Медиана"] - sql_stats["median"]) < 0.01:
        matches += 1

    if api_response["2_Использованные_данные"]["Количество_наблюдений"] == sql_stats["n"]:
        matches += 1

    return matches / total


def run_test():
    scores = []

    for case in TEST_CASES:
        response = requests.post(BASE_URL, json=case).json()

        enstru = case["query"].split()[3]
        year = int(case["query"].split()[4])

        sql_stats = price_anomaly_analysis(enstru, year)

        score = compare_numbers(response, sql_stats)
        scores.append(score)

    accuracy = sum(scores) / len(scores)

    print("Accuracy:", round(accuracy * 100, 2), "%")


if __name__ == "__main__":
    run_test()