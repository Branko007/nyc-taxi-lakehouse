{{ config(materialized='view') }}

SELECT
    -- Identificadores
    CAST(VendorID AS INT64) as vendor_id,
    CAST(RatecodeID AS INT64) as rate_code_id,
    CAST(PULocationID AS INT64) as pu_location_id,
    CAST(DOLocationID AS INT64) as do_location_id,

    -- Fechas (Convertidas de nanosegundos a Timestamp)
    TIMESTAMP_MICROS(CAST(tpep_pickup_datetime / 1000 AS INT64)) as pickup_datetime,
    TIMESTAMP_MICROS(CAST(tpep_dropoff_datetime / 1000 AS INT64)) as dropoff_datetime,

    -- Detalles del viaje
    CAST(passenger_count AS INT64) as passenger_count,
    CAST(trip_distance AS FLOAT64) as trip_distance,
    CAST(store_and_fwd_flag AS STRING) as store_and_fwd_flag,

    -- Pagos y montos (Explícitamente FLOAT64)
    CAST(payment_type AS INT64) as payment_type,
    CAST(fare_amount AS FLOAT64) as fare_amount,
    CAST(extra AS FLOAT64) as extra,
    CAST(mta_tax AS FLOAT64) as mta_tax,
    CAST(tip_amount AS FLOAT64) as tip_amount,
    CAST(tolls_amount AS FLOAT64) as tolls_amount,
    CAST(improvement_surcharge AS FLOAT64) as improvement_surcharge,
    CAST(total_amount AS FLOAT64) as total_amount,
    CAST(congestion_surcharge AS FLOAT64) as congestion_surcharge,
    CAST(Airport_fee AS FLOAT64) as airport_fee,

    -- Auditoría
    CAST(ingestion_timestamp AS TIMESTAMP) as ingestion_timestamp
FROM {{ source('raw_data', 'external_yellow_taxi') }}
