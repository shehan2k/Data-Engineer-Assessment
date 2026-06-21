import os
import pandas as pd
import duckdb

# Define Cleaned Data Input Source
cleaned_csv_path = r"d:/Data Engineer Assessment/Cleaned data/listingscsvgz_cleaned.csv"
db_path = r"d:/Data Engineer Assessment/london/analytics_warehouse.db"

# Ensure Output Directory Exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

print("🔄 Initialize Database Connection Engine...")
con = duckdb.connect(db_path)

# Drop tables if they exist to ensure clean deployment reproducibility
con.execute("DROP TABLE IF EXISTS Fact_Listings_Performance;")
con.execute("DROP TABLE IF EXISTS Dim_Property;")
con.execute("DROP TABLE IF EXISTS Dim_Host;")
con.execute("DROP TABLE IF EXISTS Dim_Location;")

# -------------------------------------------------------------
# DDL Generation Stage
# -------------------------------------------------------------
print("🏗️ Creating Dimension and Fact tables...")

con.execute("""
    CREATE TABLE Dim_Property (
        property_key VARCHAR PRIMARY KEY,
        room_type VARCHAR,
        accommodates INTEGER,
        bedrooms FLOAT,
        beds FLOAT
    );
""")

con.execute("""
    CREATE TABLE Dim_Host (
        host_key VARCHAR PRIMARY KEY,
        host_name VARCHAR,
        host_is_superhost VARCHAR
    );
""")

con.execute("""
    CREATE TABLE Dim_Location (
        location_key VARCHAR PRIMARY KEY,
        neighbourhood VARCHAR,
        latitude DOUBLE,
        longitude DOUBLE
    );
""")

con.execute("""
    CREATE TABLE Fact_Listings_Performance (
        fact_key VARCHAR PRIMARY KEY,
        property_key VARCHAR REFERENCES Dim_Property(property_key), -- 🌟 Fixed: Removed 'FOREIGN KEY'
        host_key VARCHAR REFERENCES Dim_Host(host_key),             -- 🌟 Fixed: Removed 'FOREIGN KEY'
        location_key VARCHAR REFERENCES Dim_Location(location_key), -- 🌟 Fixed: Removed 'FOREIGN KEY'
        price DOUBLE,
        minimum_nights INTEGER,
        maximum_nights INTEGER,
        availability_365 INTEGER,
        number_of_reviews INTEGER,
        reviews_per_month DOUBLE
    );
""")


# -------------------------------------------------------------
# ETL Pipeline & Ingestion Processing Stage
# -------------------------------------------------------------
print("📥 Ingesting source files into staging layout...")
# Read directly from pandas-cleaned source schema
raw_staging = pd.read_csv(cleaned_csv_path, encoding='latin1')

# Populate Dim_Property (Deduping on property_key/id)
print("✨ Populating Dim_Property...")
con.execute("""
    INSERT INTO Dim_Property
    SELECT DISTINCT 
        CAST(id AS VARCHAR) AS property_key,
        room_type,
        CAST(accommodates AS INTEGER) AS accommodates,
        CAST(bedrooms AS FLOAT) AS bedrooms,
        CAST(beds AS FLOAT) AS beds
    FROM raw_staging;
""")

# Populate Dim_Host (Deduping on host_id)
print("✨ Populating Dim_Host...")
con.execute("""
    INSERT INTO Dim_Host
    SELECT DISTINCT 
        CAST(host_id AS VARCHAR) AS host_key,
        host_name,
        host_is_superhost
    FROM raw_staging;
""")

# Populate Dim_Location (Deduping on coordinate maps or surrogate values)
print("✨ Populating Dim_Location...")
con.execute("""
    INSERT INTO Dim_Location
    SELECT DISTINCT 
        MD5(CONCAT(COALESCE(neighbourhood, 'Unknown'), '_', CAST(latitude AS VARCHAR), '_', CAST(longitude AS VARCHAR))) AS location_key,
        neighbourhood_cleansed AS neighbourhood,
        CAST(latitude AS DOUBLE) AS latitude,
        CAST(longitude AS DOUBLE) AS longitude
    FROM raw_staging;
""")

# Populate Fact Table
print("✨ Populating Central Fact Table...")
con.execute("""
    INSERT INTO Fact_Listings_Performance
    SELECT 
        CAST(id AS VARCHAR) AS fact_key,
        CAST(id AS VARCHAR) AS property_key,
        CAST(host_id AS VARCHAR) AS host_key,
        MD5(CONCAT(COALESCE(neighbourhood, 'Unknown'), '_', CAST(latitude AS VARCHAR), '_', CAST(longitude AS VARCHAR))) AS location_key,
        CAST(price AS DOUBLE) AS price,
        CAST(minimum_nights AS INTEGER) AS minimum_nights,
        CAST(maximum_nights AS INTEGER) AS maximum_nights,
        CAST(availability_365 AS INTEGER) AS availability_365,
        CAST(number_of_reviews AS INTEGER) AS number_of_reviews,
        CAST(reviews_per_month AS DOUBLE) AS reviews_per_month
    FROM raw_staging;
""")

print(f"🎉 Database Architecture built completely! Saved at: {db_path}")

# Run quick integrity check count summary
fact_count = con.execute("SELECT COUNT(*) FROM Fact_Listings_Performance;").fetchone()[0]
print(f"Verified rows committed to Fact Table: {fact_count:,}")
con.close()