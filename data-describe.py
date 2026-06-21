import os
import duckdb
import pandas as pd

# Define paths
input_file = r"d:/Data Engineer Assessment/london/neighbourhoods.csv"
output_file = r"d:/Data Engineer Assessment/Supplementary Files/neighbourhoodscsv.csv"

print("🚀 Profiling column cardinality limits...")

con = duckdb.connect()

# 1. Get all columns and their data types
columns_df = con.execute(f"DESCRIBE SELECT * FROM '{input_file}'").df()

profile_data = []

# 2. Iterate through columns to flag if duplicates exist
for idx, row in columns_df.iterrows():
    col_name = row['column_name']
    data_type = row['column_type']
    
    # Check if the column type is numeric
    is_numeric = any(num_type in data_type.lower() for num_type in ['int', 'double', 'float', 'decimal', 'numeric'])
    
    # Single optimized check: Flags Yes/No for duplicates and pulls a clean sample
    stats_query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(*) - COUNT("{col_name}") as null_count,
            CASE 
                WHEN COUNT("{col_name}") > COUNT(DISTINCT "{col_name}") THEN 'Yes' 
                ELSE 'No' 
            END as duplicates_exist,
            MIN(TRY_CAST("{col_name}" AS DOUBLE)) as min_val,
            MAX(TRY_CAST("{col_name}" AS DOUBLE)) as max_val,
            ANY_VALUE("{col_name}") FILTER (WHERE "{col_name}" IS NOT NULL) as sample_val
        FROM '{input_file}'
    """
    
    try:
        res = con.execute(stats_query).fetchone()
        total_rows, null_count, has_duplicates, min_val, max_val, sample = res[0], res[1], res[2], res[3], res[4], res[5]
        
        if is_numeric and min_val is not None and max_val is not None:
            val_range = f"{int(min_val) if min_val.is_integer() else min_val} to {int(max_val) if max_val.is_integer() else max_val}"
        else:
            val_range = "-"
            
        sample_str = str(sample) if sample is not None else "NULL"
        
    except Exception as e:
        total_rows = "Error"
        null_count = "Error"
        has_duplicates = "Error"
        val_range = "-"
        sample_str = "Error fetching sample"

    profile_data.append({
        "Column Name": col_name,
        "Data Type": data_type,
        "Total Rows": total_rows,
        "Null Count": null_count,
        "Duplicates Exist (Cardinality)": has_duplicates,
        "Value Range": val_range,
        "Sample Value": sample_str
    })
    print(f"Processed: {col_name}")

# 3. Save profile data to a fresh CSV
df_profile = pd.DataFrame(profile_data)
df_profile.to_csv(output_file, index=False)

print(f"\n✅ Profile complete! Target data exported to:\n   {output_file}")