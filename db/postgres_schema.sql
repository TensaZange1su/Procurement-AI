CREATE TABLE IF NOT EXISTS raw_lots (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT UNIQUE,
    json_data JSONB,
    loaded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fact_lots_cleaned (
    lot_id BIGINT PRIMARY KEY,
    customer_bin VARCHAR(12),
    supplier_bin VARCHAR(12),
    enstru_code VARCHAR(20),
    region VARCHAR(255),
    quantity NUMERIC,
    unit_price NUMERIC,
    total_price NUMERIC,
    publish_date DATE,
    year INT
);