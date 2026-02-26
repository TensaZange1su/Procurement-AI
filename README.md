# Procurement AI — AI агент анализа госзакупок РК

Production-ready система анализа государственных закупок с anomaly detection, fair price analysis и LLM explainability.

---

# Архитектура системы

## Общий pipeline

OWS Goszakup API  
↓  
etl/ingest.py  
↓  
PostgreSQL (raw_lots)  
↓  
etl/transform.py  
↓  
PostgreSQL (fact_lots_cleaned)  
↓  
etl/load_clickhouse.py  
↓  
ClickHouse (fact_lots)  
↓  
backend/analytics.py  
↓  
FastAPI backend  
↓  
LLM client  
↓  
User / Frontend

---

# Компоненты системы

## 1. Data ingestion

Файл:

etl/ingest.py

Назначение:

- скачивает данные из OWS API
- использует pagination через search_after
- реализует anti-bot bypass (retry, delay, session refresh)
- сохраняет raw JSON в PostgreSQL

Источник:

https://ows.goszakup.gov.kz/v3/lots

Сохраняет в таблицу:

raw_lots

---

## 2. Storage layer

### PostgreSQL

Таблица raw_lots

Хранит полный JSON:

- source_id
- json_data

Таблица fact_lots_cleaned

Нормализованные данные:

- lot_id
- customer_bin
- supplier_bin
- enstru_code
- region
- quantity
- unit_price
- total_price
- publish_date
- year

---

### ClickHouse

Таблица fact_lots

Используется для аналитики:

- anomaly detection
- fair price analysis
- volume analysis

ClickHouse используется как OLAP engine.

---

## 3. ETL layer

etl/transform.py

Функции:

- очистка данных
- расчет unit_price
- извлечение enstru_code
- извлечение region
- нормализация publish_date

---

etl/load_clickhouse.py

Перенос данных из PostgreSQL в ClickHouse.

---

# Analytics layer

backend/analytics.py

Реализует:

## Fair price analysis

Использует:

- median
- quantiles
- IQR

Возвращает:

- median price
- Q1
- Q3
- confidence
- sample size

---

## Volume analysis

Агрегация:

- sum(quantity)
- group by year

---

## Anomaly detection

Использует метод IQR:

IQR = Q3 − Q1

Outlier если:

price > Q3 + 1.5 × IQR  
price < Q1 − 1.5 × IQR  

---

# Backend

FastAPI backend:

backend/main.py

Endpoint:

POST /query

Example request:

```json
{
  "query": "справедливая цена enstru 1046871 регион 711310000"
}
```
Swagger UI:

http://127.0.0.1:8000/docs

---

# LLM layer

## backend/llm_client.py

Назначение:

объяснение результатов

генерация аналитических выводов

LLM НЕ выполняет вычисления.
Все вычисления выполняются в ClickHouse.

---
# Структура проекта

```
procurement-ai/

backend/
    main.py
    analytics.py
    sql_builder.py
    formatter.py
    llm_client.py

etl/
    ingest.py
    transform.py
    load_clickhouse.py

requirements.txt
docker-compose.yml
README.md
```

---

# Requirements

## *Минимальные:*

Python 3.10+

PostgreSQL 14+

ClickHouse 23+

8 GB RAM

20 GB disk space


## *Рекомендуемые:*

16 GB RAM

100+ GB disk space

Linux server
---
# Python dependencies

requirement.txt
````
fastapi
uvicorn
psycopg2-binary
clickhouse-driver
requests
python-dotenv
pandas
numpy
````
---
# Установка и запуск

## 1. Клонирование проекта

```bash
git clone https://github.com/your-org/procurement-ai.git
cd procurement-ai
```
---
## 2. Cоздание Python окружения

Windows (conda)
```
conda create -n procurement python=3.10
conda activate procurement
```

Linux / Mac (venv)
```
python -m venv venv
source venv/bin/activate
```

---

## 3. Установка зависимостей
```
pip install -r requirements.txt
```
---
## 4. Запуск PostgreSQL и ClickHouse через Docker
```
docker-compose up -d
```
Проверить контенеры:
```
вщслук зы
```

Должны быть:

procurement-ai-postgres

procurement-ai-clickhouse

---
## 5. Создание таблиц PostgreSQL

Подключение:
```
docker exec -it procurement-ai-postgres psql -U admin -d procurement
```

Создать таблицы:
```
CREATE TABLE raw_lots (
    source_id BIGINT PRIMARY KEY,
    json_data JSONB
);

CREATE TABLE fact_lots_cleaned (
    lot_id BIGINT PRIMARY KEY,
    customer_bin TEXT,
    supplier_bin TEXT,
    enstru_code TEXT,
    region TEXT,
    quantity FLOAT,
    unit_price FLOAT,
    total_price FLOAT,
    publish_date DATE,
    year INT
);
```

## 6. Создание таблицы ClickHouse

Подключение:
```
docker exec -it procurement-ai-clickhouse clickhouse-client
```

Создать database:
```
CREATE DATABASE IF NOT EXISTS procurement;

Создать таблицу:

CREATE TABLE procurement.fact_lots
(
    lot_id UInt64,
    customer_bin String,
    supplier_bin String,
    enstru_code String,
    region String,
    quantity Float64,
    unit_price Float64,
    total_price Float64,
    publish_date Date,
    year UInt16
)
ENGINE = MergeTree()
ORDER BY (enstru_code, region, year);
```
----
## Запуск ETL pipeline
Step 1 — ingestion (скачивание данных)
```python etl/ingest.py```

⚠ Важно:

Полная загрузка может занимать:

до 10 часов

10 – 50 GB disk space

Это связано с anti-bot защитой API.

Step 2 — transform
```python etl/transform.py```

Step 3 — загрузка в ClickHouse
```python etl/load_clickhouse.py```

Запуск backend
```
uvicorn backend.main:app --reload
```

Swagger UI:

http://127.0.0.1:8000/docs
Тестирование API

Пример запроса:
```
curl -X POST http://127.0.0.1:8000/query \
-H "Content-Type: application/json" \
-d '{"query": "объем закупок enstru 1046871"}'
```

## Проверка ClickHouse
```
docker exec -it procurement-ai-clickhouse clickhouse-client
```
```
SELECT COUNT() FROM procurement.fact_lots;
```
## Полный production запуск
```
docker-compose up -d

python etl/ingest.py
python etl/transform.py
python etl/load_clickhouse.py

uvicorn backend.main:app --reload
```

Swagger
```http://127.0.0.1:8000/docs```s