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

print("📊 Analyzing correlation between review volume and price...")

# 2. Query extracting pricing and review volume directly from the Fact table
query = """
SELECT 
    CAST(price AS DOUBLE) AS price,
    CAST(number_of_reviews AS BIGINT) AS review_count
FROM Fact_Listings_Performance
WHERE price > 0 AND number_of_reviews IS NOT NULL;
"""

df = con.execute(query).fetchdf()
con.close()

# 3. Generate Scatter Plot with Regression Line
plt.figure(figsize=(9, 5.5))
sns.set_theme(style="whitegrid")

# Filter out extreme luxury outliers (> $500) to keep the core market volume visible
df_filtered = df[df['price'] <= 500]

# Scatter plot using a clean, single-tone color
sns.scatterplot(
    data=df_filtered,
    x='review_count',
    y='price',
    color='#34495e',
    alpha=0.4,
    edgecolor=None,
    s=25
)

# Overlay a strong trend line to clarify the pricing trajectory
sns.regplot(
    data=df_filtered,
    x='review_count',
    y='price',
    scatter=False,
    color='#e74c3c',
    line_kws={"linewidth": 2.5}
)

plt.title('Market Elasticity: Total Review Count vs. Nightly Listing Price', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Total Review Count (Booking Volume Proxy)', fontsize=11)
plt.ylabel('Nightly Price ($)', fontsize=11)

plt.tight_layout()

# Save image file
output_plot_path = os.path.join(output_dir, '14_review_count_vs_price.png')
plt.savefig(output_plot_path, dpi=300)
plt.close()

print(f"🎉 Bi-variate analysis complete! Trend plot exported to:\n👉 {output_plot_path}")