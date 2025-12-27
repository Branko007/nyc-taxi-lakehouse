{{ config(materialized='table') }}

SELECT
    pu_location_id,
    COUNT(*) as total_trips,
    AVG(trip_distance) as avg_distance,
    AVG(total_amount) as avg_price_per_trip
FROM {{ ref('silver_yellow_tripdata') }}
GROUP BY 1
ORDER BY 2 DESC
