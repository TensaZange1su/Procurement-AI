CREATE TABLE IF NOT EXISTS fact_lots
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
ENGINE = MergeTree
PARTITION BY year
ORDER BY (enstru_code, region, publish_date);