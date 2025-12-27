{{ config(materialized='table') }}

SELECT
    vendor_id,
    EXTRACT(YEAR FROM pickup_datetime) as year,
    EXTRACT(MONTH FROM pickup_datetime) as month,
    SUM(fare_amount) as total_fare,
    SUM(tip_amount) as total_tips,
    SUM(total_amount) as total_revenue,
    COUNT(*) as total_trips
FROM {{ ref('silver_yellow_tripdata') }}
GROUP BY 1, 2, 3
ORDER BY 2 DESC, 3 DESC, 1
