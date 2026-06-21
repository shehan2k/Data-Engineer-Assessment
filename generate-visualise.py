import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup paths
db_path = r"d:/Data Engineer Assessment/london/analytics_warehouse.db"
output_dir = r"d:/Data Engineer Assessment/london/plots"
os.makedirs(output_dir, exist_ok=True)

# Set global plotting style for a clean engineering look
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 13})

# Initialize DuckDB
con = duckdb.connect(db_path)

# --- 1. PREPARE THE DATA FROM WAREHOUSE ---
# Pull metrics while capping prices at $600 to cleanly visualize distribution density without extreme outliers
query = """
SELECT 
    f.price,
    l.neighbourhood,
    p.room_type,
    -- Simple fallback if property_type isn't a direct dimension column yet
    COALESCE(p.room_type, 'Other') AS property_type 
FROM Fact_Listings_Performance f
JOIN Dim_Location l ON f.location_key = l.location_key
JOIN Dim_Property p ON f.property_key = p.property_key
WHERE f.price BETWEEN 1 AND 600;
"""
df = con.execute(query).fetchdf()
con.close()

# Identify top 10 most dense neighbourhoods to keep the chart clean and readable
top_neighbourhoods = df['neighbourhood'].value_counts().head(10).index
df_top_loc = df[df['neighbourhood'].isin(top_neighbourhoods)]

# --- VISUALIZATION 1: OVERALL CITY PRICE DISTRIBUTION (Density & Spread) ---
print("🎨 Plotting 1: City Market Density...")
plt.figure(figsize=(10, 5))
sns.histplot(data=df, x='price', kde=True, color='#2bc48a', bins=50, alpha=0.6)
plt.axvline(df['price'].median(), color='red', linestyle='--', label=f"Median Price: ${df['price'].median():.0f}")
plt.axvline(df['price'].mean(), color='blue', linestyle='-.', label=f"Mean Price: ${df['price'].mean():.0f}")
plt.title('Overall Market Price Distribution & Density (London Context)', fontweight='bold')
plt.xlabel('Nightly Price ($)')
plt.ylabel('Listing Count Frequency')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '1_city_price_distribution.png'), dpi=300)
plt.close()

# --- VISUALIZATION 2: NEIGHBOURHOOD COMPARISON (Top 10 High-Density Boroughs) ---
print("🎨 Plotting 2: Price by Neighbourhood...")
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_top_loc, x='price', y='neighbourhood', palette='Spectral', order=top_neighbourhoods)
plt.title('Price Variances Across Top 10 London Boroughs (By Listing Density)', fontweight='bold')
plt.xlabel('Nightly Price ($)')
plt.ylabel('Borough / Neighbourhood')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '2_price_by_neighbourhood.png'), dpi=300)
plt.close()

# --- VISUALIZATION 3: ROOM TYPE PRICE DISTRIBUTIONS (Violin Overlay) ---
print("🎨 Plotting 3: Price by Room Type...")
plt.figure(figsize=(10, 6))
# Violin plots elegantly capture both the boxplot markers and structural multi-modal curves
sns.violinplot(data=df, x='room_type', y='price', palette='Set2', inner='quartile')
plt.title('Price Structural Distribution Velocity by Room Type Layout', fontweight='bold')
plt.xlabel('Room Configuration Type')
plt.ylabel('Nightly Price ($)')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '3_price_by_room_type.png'), dpi=300)
plt.close()

# --- VISUALIZATION 4: PROPERTY CONFIGURATION TYPE MATRIX ---
print("🎨 Plotting 4: Price by Property Type Segment...")
plt.figure(figsize=(10, 5))
sns.kdeplot(data=df, x='price', hue='room_type', fill=True, common_norm=False, palette='Set2', alpha=0.4)
plt.title('Price Distribution Probabilities by Property Segmentation', fontweight='bold')
plt.xlabel('Nightly Price ($)')
plt.ylabel('Probability Density Variance')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '4_price_by_property_segment.png'), dpi=300)
plt.close()

print(f"🎉 Success! All 4 analytical distribution plots exported to: {output_dir}")