import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_path = r"d:/Data Engineer Assessment/london/hosting_location.csv"

# 1. Load the dataset safely
print("🔄 Ingesting dataset...")
df = pd.read_csv(csv_path, encoding='latin1', on_bad_lines='skip')

price_col = 'listings'
loc_col = 'location'

# 2. Clean data and convert price to numeric
df['clean_numeric'] = pd.to_numeric(df[price_col], errors='coerce')
df = df.dropna(subset=['clean_numeric', loc_col])

# Filter down to the Top 10 neighborhoods so the X-axis stays clean and readable
top_neighborhoods = df[loc_col].value_counts().nlargest(10).index
df_filtered = df[df[loc_col].isin(top_neighborhoods)].copy()

# Cap at 1000 to keep the vertical axis from compressing standard listings
df_filtered = df_filtered[df_filtered['clean_numeric'] <= 1000]

# 3. Create Hosting Range Categories for Color Mapping
host_bins = [0, 50, 100, 200, 300, 400, 500]
host_labels = ['1-50 Listings', '51-100 Listings', '101-200 Listings', '201-300 Listings', '301-400 Listings', '401-500 Listings']
df_filtered['Hosting Range'] = pd.cut(df_filtered['clean_numeric'], bins=host_bins, labels=host_labels)

# Drop rows that don't fall into the bins (e.g., if any values are > 500)
df_filtered = df_filtered.dropna(subset=['Hosting Range'])

# 4. Generate the Scatter Plot
plt.figure(figsize=(14, 8))

# Map neighborhood names to numeric positions (0, 1, 2...) for plotting
neighborhood_mapping = {name: i for i, name in enumerate(top_neighborhoods)}
df_filtered['x_pos'] = df_filtered[loc_col].map(neighborhood_mapping)

# Add horizontal jitter so the scatter dots spread out into clear distinct columns
x_jitter = df_filtered['x_pos'] + np.random.normal(0, 0.15, size=len(df_filtered))

# 🌟 FIX: Colors mapped to match your exact host_labels keys
colors = {
    '1-50 Listings': '#2ecc71',       # Green
    '51-100 Listings': '#3498db',     # Blue
    '101-200 Listings': '#9b59b6',    # Purple
    '201-300 Listings': '#f1c40f',    # Yellow
    '301-400 Listings': '#e67e22',    # Orange
    '401-500 Listings': '#e74c3c'     # Red
}

# 🌟 FIX: Changed 'labels' loop to use 'host_labels' and 'Hosting Range' column
for segment in host_labels:
    mask = df_filtered['Hosting Range'] == segment
    segment_data = df_filtered[mask]
    segment_jitter = x_jitter[mask]
    
    # Only plot if there is data in this bracket to avoid empty legend warnings
    if not segment_data.empty:
        plt.scatter(
            segment_jitter, 
            segment_data['clean_numeric'], 
            alpha=0.4,                           # Transparency reveals cluster density
            c=colors[segment], 
            label=segment, 
            edgecolors='none', 
            s=15
        )

# 5. Customizing the Layout and Axes
plt.title('Scatter Distribution of Hostings across Top London Locations', fontsize=14, fontweight='bold', pad=20)
plt.ylabel('Number of Listings / Hostings Count', fontsize=11, labelpad=10)
plt.xlabel('Location', fontsize=11, labelpad=12)

# Map the numeric X positions back to the actual neighborhood text strings safely
plt.xticks(range(len(top_neighborhoods)), top_neighborhoods, rotation=35, ha='right', fontsize=10)
plt.ylim(0, 550)  # Dynamic ceiling matching your highest bin cutoff (500)

# Add structural gridlines behind the dots
plt.grid(axis='y', linestyle='--', alpha=0.4)

# Create a clean interactive legend block
# Make legend icons solid so they are easy to read

plt.tight_layout()
plt.show()