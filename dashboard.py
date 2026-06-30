# dashboard.py
import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(page_title="Eras Tour Warehouse Insights", layout="wide")
st.title("🎤 Taylor Swift Concert Tours - Warehouse Analytics")
st.markdown("Architected completely via **DuckDB** and **dbt** (Medallion Structure Data Marts)")

# 🌟 STEP 1: Wrap connection configuration in a resource cache block
@st.cache_resource
def get_database_connection():
    # Re-use a single read-only pointer globally across all app refreshes
    return duckdb.connect("swift_analytics/database.duckdb", read_only=True)

# Call the cached function instead of opening raw connections directly
conn = get_database_connection()

# 📊 STEP 2: Fetch Key Data Warehouse KPI Metrics
kpi_df = conn.execute("""
    SELECT 
        SUM(tickets_sold) as total_tickets,
        SUM(total_revenue) as gross_revenue,
        AVG(avg_ticket_price) as global_avg_ticket_price
    FROM fct_concert_sales
""").df()

# Render High-Level Statistics Grid
col1, col2, col3 = st.columns(3)
col1.metric("Total Tickets Sold", f"{int(kpi_df['total_tickets'][0]):,}")
col2.metric("Total Gross Revenue", f"${kpi_df['gross_revenue'][0]:,.2f}")
col3.metric("Average Ticket Price", f"${kpi_df['global_avg_ticket_price'][0]:,.2f}")

st.markdown("---")

# STEP 3: Add Tour Performance Breakdown Chart
st.subheader("Gross Revenue Performance Across Concert Tours")
revenue_df = conn.execute("""
    SELECT tour_name, SUM(total_revenue) as revenue
    FROM fct_concert_sales
    GROUP BY tour_name
    ORDER BY revenue DESC
""").df()

fig = px.bar(
    revenue_df, 
    x='tour_name', 
    y='revenue', 
    labels={'revenue':'Revenue ($)', 'tour_name':'Tour Name'}, 
    template="plotly_dark",
    color='revenue',
    color_continuous_scale='Purples'
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# STEP 4: Add Top Venues Table Data Mart View
st.subheader("🏆 Top 5 Venues by Ticket Sales Volume")
venue_efficiency = conn.execute("""
    SELECT 
        v.venue_name AS "Venue Name", 
        v.city AS "City", 
        v.country AS "Country",
        SUM(f.tickets_sold) AS "Total Tickets Sold", 
        ROUND(AVG(f.avg_ticket_price), 2) AS "Average Ticket Price ($)"
    FROM fct_concert_sales f
    JOIN dim_venues v ON f.venue_key = v.venue_key
    GROUP BY v.venue_name, v.city, v.country
    ORDER BY SUM(f.tickets_sold) DESC
    LIMIT 5
""").df()

st.dataframe(venue_efficiency, use_container_width=True, hide_index=True)