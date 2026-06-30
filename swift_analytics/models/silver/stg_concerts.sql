{{ config(materialized='view') }}

WITH base_data AS (
    SELECT *,
           -- Generate an incrementing window counter for identical venues/tours
           ROW_NUMBER() OVER (PARTITION BY Tour, City, Venue ORDER BY "Attendance (tickets sold / available)") as session_number
    FROM {{ ref('raw_concerts') }}
)

SELECT
    -- Include the session number variant so Night 1 and Night 2 get unique hashes
    md5(concat(coalesce(Tour, ''), '-', coalesce(City, ''), '-', coalesce(Venue, ''), '-', CAST(session_number AS VARCHAR))) AS concert_id,
    TRIM(Tour) AS tour_name,
    TRIM(Venue) AS venue_name,
    TRIM(City) AS city,
    TRIM(Country) AS country,
    
    CASE 
        WHEN "Attendance (tickets sold / available)" LIKE '%/%' 
        THEN CAST(REPLACE(STR_SPLIT("Attendance (tickets sold / available)", ' / ')[1], ',', '') AS INT)
        ELSE NULL
    END AS tickets_sold,

    CASE 
        WHEN "Attendance (tickets sold / available)" LIKE '%/%' 
        THEN CAST(REPLACE(STR_SPLIT("Attendance (tickets sold / available)", ' / ')[2], ',', '') AS INT)
        ELSE NULL
    END AS tickets_available,
    
    CASE 
        WHEN Revenue IS NULL OR TRIM(Revenue) IN ('—', '') THEN 0.00
        ELSE CAST(REPLACE(REPLACE(Revenue, '$', ''), ',', '') AS DECIMAL(12, 2))
    END AS total_revenue

FROM base_data
WHERE "Attendance (tickets sold / available)" IS NOT NULL 
  AND "Attendance (tickets sold / available)" NOT IN ('—', '')