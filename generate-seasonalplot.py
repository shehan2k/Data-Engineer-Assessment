import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration paths
db_path = r"d:/Data Engineer Assessment/london/analytics_warehouse.db"
output_dir = r"d:/Data Engineer Assessment/london/plots"
os.makedirs(output_dir, exist_ok=True)

# 1. Connect to DuckDB warehouse
con = duckdb.connect(db_path)

print("📊 Analyzing host portfolio distribution architectures...")

# 2. Query counting listings per host using production dimension keys
query = """
SELECT 
    h.host_key,
    COUNT(f.fact_key) AS portfolio_size,
    AVG(f.price) AS avg_nightly_price
FROM Fact_Listings_Performance f
JOIN Dim_Host h ON f.host_key = h.host_key
GROUP BY h.host_key;
"""

df_hosts = con.execute(query).fetchdf()
con.close()

# 3. Apply operational segment classifications
df_hosts['host_segment'] = df_hosts['portfolio_size'].apply(
    lambda x: 'Single-Listing Operator' if x == 1 else 'Multi-Listing Commercial'
)

# Calculate segment volumes for plot labelling
segment_counts = df_hosts['host_segment'].value_counts()

# 4. Generate Visual Share Chart
plt.figure(figsize=(8, 5))
sns.set_theme(style="whitegrid")

sns.barplot(
    x=segment_counts.index, 
    y=segment_counts.values, 
    palette='muted',
    hue=segment_counts.index,
    legend=False
)

plt.title('Market Composition: Single-Listing vs. Multi-Listing Commercial Hosts', fontsize=13, fontweight='bold', pad=12)
plt.xlabel('Host Operational Segment', fontsize=11)
plt.ylabel('Total Unique Hosts (Count)', fontsize=11)

plt.tight_layout()

# Save image file
output_plot_path = os.path.join(output_dir, '11_host_portfolio_segmentation.png')
plt.savefig(output_plot_path, dpi=300)
plt.close()

print(f"🎉 Host portfolio segmentation complete! Plot exported to:\n👉 {output_plot_path}")