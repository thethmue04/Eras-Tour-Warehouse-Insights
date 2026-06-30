{{ config(materialized='table') }}

SELECT
    concert_id,
    md5(concat(coalesce(venue_name, ''), '-', coalesce(city, ''))) AS venue_key,
    tour_name,
    tickets_sold,
    tickets_available,
    (tickets_available - tickets_sold) AS unsold_tickets,
    total_revenue,
    CASE 
        WHEN tickets_sold > 0 THEN ROUND(total_revenue / tickets_sold, 2)
        ELSE 0.00
    END AS avg_ticket_price
FROM {{ ref('stg_concerts') }}