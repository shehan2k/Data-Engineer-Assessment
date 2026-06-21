import duckdb

# Connect to your newly created data warehouse
con = duckdb.connect(r"d:/Data Engineer Assessment/london/analytics_warehouse.db")

print("📊 Running Use Case 1: Market Concentration Analysis...")
query_1 = """
SELECT 
    h.host_name,
    COUNT(f.fact_key) AS total_managed_properties,
    ROUND(AVG(f.price), 2) AS average_nightly_rate,
    ROUND(SUM(f.price * f.availability_365), 2) AS max_annual_revenue_potential
FROM Fact_Listings_Performance f
JOIN Dim_Host h ON f.host_key = h.host_key
GROUP BY h.host_name
HAVING total_managed_properties > 1
ORDER BY max_annual_revenue_potential DESC
LIMIT 5;
"""

# Fetch and display the results cleanly as a dataframe
df_results = con.execute(query_1).fetchdf()
print(df_results)

con.close()