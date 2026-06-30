{{ config(materialized='table') }}

SELECT DISTINCT
    md5(concat(coalesce(venue_name, ''), '-', coalesce(city, ''))) AS venue_key,
    venue_name,
    city,
    country
FROM {{ ref('stg_concerts') }}