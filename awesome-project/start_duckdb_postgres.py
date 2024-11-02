import duckdb

# Path to your DuckDB database
DB_PATH = "/home/rob/Documents/simple-gateway/awesome-project/devices.duckdb"  # Replace with your actual path

# Start DuckDB and enable the PostgreSQL wire protocol on port 5433
conn = duckdb.connect(database=DB_PATH)
conn.execute("INSTALL postgres_scanner; LOAD postgres_scanner;")
conn.execute("EXPORT DATABASE 'postgres://localhost:5433'")