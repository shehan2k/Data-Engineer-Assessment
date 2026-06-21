import os
import pandas as pd
import numpy as np

# Define Paths
input_file = r"d:/Data Engineer Assessment/london/reviews.csv.gz"
output_file = r"d:/Data Engineer Assessment/Cleaned data/reviewscsvgz_cleaned.csv"

print("🔄 Ingesting raw dataset...")
# low_memory=False ensures stable data type inference across millions of fields
df = pd.read_csv(input_file, encoding='latin1', on_bad_lines='skip', low_memory=False)

# Validation log dictionary to keep track of decisions/records dropped
validation_log = {
    "Total Raw Records Ingested": len(df),
    "Dropped: Missing Price": 0,
    "Dropped: Corrupted Price Format": 0,
    "Dropped: Negative / Zero Price": 0,
    "Dropped: Invalid Geographic Coordinates": 0
}

# -------------------------------------------------------------
# 1. Standardize Price Columns
# -------------------------------------------------------------
print("🧹 Standardizing price column...")
if 'price' in df.columns:
    # Safely convert to string, remove currency symbols ($), spaces, and thousands separators (commas)
    df['clean_price'] = df['price'].astype(str).str.replace(r'[$,\s]', '', regex=True)
    
    # Cast to numeric, turning text violations into NaN
    df['clean_price'] = pd.to_numeric(df['clean_price'], errors='coerce')
    
    # Flag and remove records that fail validation rules
    initial_count = len(df)
    validation_log["Dropped: Missing Price"] = int(df['price'].isna().sum())
    
    # Filter rules: Prices must be numeric, present, and strictly greater than 0
    df = df[df['clean_price'].notna()]
    validation_log["Dropped: Corrupted Price Format"] = int(initial_count - len(df) - validation_log["Dropped: Missing Price"])
    
    post_numeric_count = len(df)
    df = df[df['clean_price'] > 0]
    validation_log["Dropped: Negative / Zero Price"] = int(post_numeric_count - len(df))
    
    # Replace original column
    df = df.drop(columns=['price']).rename(columns={'clean_price': 'price'})

# -------------------------------------------------------------
# 2. Parse and Standardize Date Fields
# -------------------------------------------------------------
print("📅 Standardizing date fields...")
date_cols = ['last_review']  # Add other date columns if present in your additional files

for col in date_cols:
    if col in df.columns:
        # Parse flexible dates format dynamically and standardize to ISO format (YYYY-MM-DD)
        df[col] = pd.to_datetime(df[col], errors='coerce')

# -------------------------------------------------------------
# 3. Normalize Free-Text Fields into Categorical Values
# -------------------------------------------------------------
print("🗂️ Normalizing categorical values...")
# Lowercase, trim spaces, and handle casing variances
categorical_cols = ['room_type', 'neighbourhood']

for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.title()
        # Handle sentinel assignments for unexpected blanks in categorical fields
        df[col] = df[col].replace({'Nan': 'Unknown', 'None': 'Unknown', '': 'Unknown'})

# -------------------------------------------------------------
# 4. Handle Missing Values with Explicit Strategies
# -------------------------------------------------------------
print("🛠️ Managing missing values...")
# Sentinel value strategy for missing structural counts
if 'calculated_host_listings_count' in df.columns:
    df['calculated_host_listings_count'] = df['calculated_host_listings_count'].fillna(-1).astype(int)

if 'availability_365' in df.columns:
    df['availability_365'] = df['availability_365'].fillna(-1).astype(int)

# Explicit null strategy / Imputation for reviews
if 'reviews_per_month' in df.columns:
    # Impute missing monthly review velocities with 0.0 if no reviews exist
    df['reviews_per_month'] = df['reviews_per_month'].fillna(0.0).astype(float)

# -------------------------------------------------------------
# 5. Standardize Geographic Fields & Coordinate Precision
# -------------------------------------------------------------
print("📍 Standardizing geographic fields and coordinate precision...")
# Enforce a high scientific decimal point precision standard (5 decimal places is precise up to ~1.1 meters)
coordinate_precision = 5

if 'latitude' in df.columns and 'longitude' in df.columns:
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    # Validate coordinate boundaries (London coordinates boundaries bounding box validation)
    geo_mask = (df['latitude'].between(51.0, 52.0)) & (df['longitude'].between(-1.0, 1.0))
    validation_log["Dropped: Invalid Geographic Coordinates"] = int((~geo_mask).sum())
    df = df[geo_mask]
    
    # Truncate / round coordinate precision uniformly
    df['latitude'] = df['latitude'].round(coordinate_precision)
    df['longitude'] = df['longitude'].round(coordinate_precision)

# -------------------------------------------------------------
# 6. Export Clean Data & Document Decisions
# -------------------------------------------------------------
print("\n💾 Exporting target dataset and creating validation documentation...")
# Enforce explicit string quoting parameters to protect against unquoted text comma separation shifting
df.to_csv(output_file, index=False, encoding='utf-8', quoting=1)

print("\n📋 --- ASSESSMENT DATA ARCHITECTURE VALIDATION LOG ---")
for key, val in validation_log.items():
    print(f"👉 {key}: {val:,}")
print(f"🌟 Final Usable Clean Records Saved: {len(df):,}")
print("--------------------------------------------------------")