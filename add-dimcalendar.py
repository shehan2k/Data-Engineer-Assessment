import duckdb

# Path to your existing database and the new data file
db_path = r"d:/Data Engineer Assessment/london/analytics_warehouse.db"
new_data_csv = r"d:/Data Engineer Assessment/Cleaned data/calendar_cleaned.csv"

# 1. Connect to your existing database
con = duckdb.connect(db_path)

print("⏳ Creating and loading the new table...")

# 2. Run a standard SQL query to create the table straight from the CSV
# DuckDB automatically infers column names and data types from the file
con.execute(f"""
    CREATE TABLE IF NOT EXISTS Dim_Calendar_New AS 
    SELECT * FROM read_csv_auto('{new_data_csv}');
""")

# 3. Verify the table was added successfully
print("🔍 Verifying warehouse tables:")
print(con.execute("SHOW TABLES;").fetchdf())

# 4. Close the connection
con.close()
print("🎉 Success! New table added to the analytics warehouse.")