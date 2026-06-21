import os
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Database configuration
db_path = r"d:/Data Engineer Assessment/london/analytics_warehouse.db"
output_dir = r"d:/Data Engineer Assessment/london/plots"
os.makedirs(output_dir, exist_ok=True)

con = duckdb.connect(db_path)

print("📊 1. Computing Descriptive Statistics for Key Numerical Variables...")
desc_query = """
SELECT 
    'price' AS metric, AVG(price) AS mean, MIN(price) AS min, MAX(price) AS max, STDDEV(price) AS std_dev FROM Fact_Listings_Performance WHERE price > 0
UNION ALL
SELECT 
    'availability_365' AS metric, AVG(availability_365), MIN(availability_365), MAX(availability_365), STDDEV(availability_365) FROM Fact_Listings_Performance WHERE availability_365 >= 0
UNION ALL
SELECT 
    'number_of_reviews' AS metric, AVG(number_of_reviews), MIN(number_of_reviews), MAX(number_of_reviews), STDDEV(number_of_reviews) FROM Fact_Listings_Performance;
"""
df_desc = con.execute(desc_query).fetchdf()
print("\n--- Summary Statistics Table ---")
print(df_desc.to_string(index=False))


print("\n🎨 2. Visualizing Price Distributions by Room Type...")
# We filter up to $500 to keep the distribution chart dense and highly readable
price_room_query = """
SELECT f.price, p.room_type 
FROM Fact_Listings_Performance f
JOIN Dim_Property p ON f.property_key = p.property_key
WHERE f.price BETWEEN 1 AND 500;
"""
df_price_room = con.execute(price_room_query).fetchdf()

plt.figure(figsize=(10, 6))
sns.boxplot(data=df_price_room, x='room_type', y='price', palette='Set2')
plt.title('Price Distribution by Room Type (Capped at $500)', fontsize=12, fontweight='bold')
plt.xlabel('Room Type')
plt.ylabel('Nightly Price ($)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'price_by_room_type.png'))
plt.close()


print("📈 3. Analyzing Power Law Dynamics in Hosting (Listing counts per Host)...")
host_dist_query = """
SELECT total_properties, COUNT(host_key) AS host_count
FROM (
    SELECT host_key, COUNT(fact_key) AS total_properties
    FROM Fact_Listings_Performance
    GROUP BY host_key
)
GROUP BY total_properties
ORDER BY total_properties ASC;
"""
df_host_dist = con.execute(host_dist_query).fetchdf()

plt.figure(figsize=(10, 6))
plt.bar(df_host_dist['total_properties'].head(15), df_host_dist['host_count'].head(15), color='#34495e', alpha=0.85)
plt.title('Hosting Distribution: Listing Volume per Unique Host (Long-Tail View)', fontsize=12, fontweight='bold')
plt.xlabel('Number of Properties Owned by a Single Host')
plt.ylabel('Count of Unique Hosts (Log Scale)')
plt.yscale('log') # Power law distributions look clearest on log scales
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'hosting_power_law.png'))
plt.close()


print("⭐ 4. Examining Review Score Distributions for Rating Inflation...")
# Pull the review metrics from your warehouse staging data or fact properties
review_query = """
SELECT number_of_reviews, reviews_per_month 
FROM Fact_Listings_Performance 
WHERE number_of_reviews > 0;
"""
df_reviews = con.execute(review_query).fetchdf()

plt.figure(figsize=(10, 6))
sns.histplot(df_reviews['reviews_per_month'].dropna(), bins=50, kde=True, color='#e74c3c')
plt.title('Distribution of Review Pacing (Reviews per Month)', fontsize=12, fontweight='bold')
plt.xlabel('Reviews Per Month')
plt.ylabel('Frequency Density')
plt.xlim(0, 10)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'review_distribution.png'))
plt.close()

print(f"🎉 Analysis plots successfully exported to: {output_dir}")
con.close()