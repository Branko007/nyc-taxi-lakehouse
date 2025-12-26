{{ config(
    materialized='incremental',
    unique_key=['vendor_id', 'pickup_datetime', 'dropoff_datetime', 'pu_location_id', 'do_location_id'],
    incremental_strategy='merge'
) }}

WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY vendor_id, pickup_datetime, dropoff_datetime, pu_location_id, do_location_id
            ORDER BY ingestion_timestamp DESC
        ) as row_num
    FROM {{ ref('stg_yellow_tripdata') }}
    WHERE trip_distance > 0 
      AND fare_amount > 0
      AND pickup_datetime < CURRENT_TIMESTAMP()
)

SELECT
    * EXCEPT(row_num)
FROM deduplicated
WHERE row_num = 1

{% if is_incremental() %}
  -- Este filtro asegura que solo procesemos datos nuevos si es necesario
  AND ingestion_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
{% endif %}
