import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_path = r"d:/Data Engineer Assessment/london/price_availability.csv"

# 1. Load the dataset safely
print("🔄 Ingesting dataset...")
df = pd.read_csv(csv_path, encoding='latin1', on_bad_lines='skip')

price_col = 'price'
host_col = 'hostings' 

# 2. Clean data and force both columns to be strictly numeric
df['clean_numeric_price'] = pd.to_numeric(df[price_col], errors='coerce')
df['clean_numeric_host'] = pd.to_numeric(df[host_col], errors='coerce')
df = df.dropna(subset=['clean_numeric_price', 'clean_numeric_host'])

# Cap at $1000 to keep the vertical axis clean
df_filtered = df[df['clean_numeric_price'] <= 1000].copy()

# 3. Create Categories for BOTH Axes
# Y-Axis Price Brackets
price_bins = [0, 75, 150, 250, 500, 1000]
price_labels = ['Budget ($0-75)', 'Standard ($76-150)', 'Premium ($151-250)', 'Luxury ($251-500)', 'Ultra Luxury ($501-1000)']
df_filtered['Price Segment'] = pd.cut(df_filtered['clean_numeric_price'], bins=price_bins, labels=price_labels)

# X-Axis Capacity Brackets (Hostings Range)
host_bins = [0, 50, 100, 200, 300, 400, 500]
host_labels = ['1-50 Listings', '51-100 Listings', '101-200 Listings', '201-300 Listings', '301-400 Listings', '401-500 Listings']
df_filtered['Hosting Range'] = pd.cut(df_filtered['clean_numeric_host'], bins=host_bins, labels=host_labels)

# Drop any rows that fell outside our bracket ranges
df_filtered = df_filtered.dropna(subset=['Price Segment', 'Hosting Range'])

# 4. Map the X-Axis Categories to Numerical Positions for Jittering
host_mapping = {label: i for i, label in enumerate(host_labels)}
df_filtered['x_pos'] = df_filtered['Hosting Range'].map(host_mapping).astype(float)

# Add random horizontal jitter so dots spread out inside their specific range column
x_jitter = df_filtered['x_pos'] + np.random.normal(0, 0.15, size=len(df_filtered))

# 5. Generate the Scatter Plot
plt.figure(figsize=(13, 8))

colors = {
    'Budget ($0-75)': '#2ecc71',        # Green
    'Standard ($76-150)': '#3498db',     # Blue
    'Premium ($151-250)': '#f1c40f',     # Yellow
    'Luxury ($251-500)': '#e67e22',      # Orange
    'Ultra Luxury ($501-1000)': '#e74c3c' # Red
}

# Plot each segment so they format properly in the legend
for segment in price_labels:
    mask = df_filtered['Price Segment'] == segment
    
    plt.scatter(
        x_jitter[mask], 
        df_filtered.loc[mask, 'clean_numeric_price'], # Keeping exact price vertically
        alpha=0.25,                                   # Transparency shows true data density
        c=colors[segment], 
        label=segment, 
        edgecolors='none', 
        s=12
    )

# 6. Customizing the Layout and Axes
plt.title('Scatter Distribution of Prices across Listing Brackets', fontsize=14, fontweight='bold', pad=20)
plt.ylabel('Exact Nightly Price ($)', fontsize=11, labelpad=10)
plt.xlabel('Accommodation Listing Bracket', fontsize=11, labelpad=12)

# Replace the 0, 1, 2... X-axis numbers with your clean capacity text ranges
plt.xticks(range(len(host_labels)), host_labels, fontsize=10)
plt.ylim(0, 1050)

# Structural gridlines
plt.grid(axis='y', linestyle='--', alpha=0.4)

# Formatting the legend block
 

plt.tight_layout()
plt.show()