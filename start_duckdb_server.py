import duckdb

# Path to your DuckDB database
DB_PATH = "/home/rob/Downloads/Grafana-dashboards-and-query-script/devices.duckdb"  # Adjust this path

# Start DuckDB in server mode on port 5433
conn = duckdb.connect(database=DB_PATH)
conn.execute("INSTALL postgres_scanner; LOAD postgres_scanner;")
conn.execute("EXPORT DATABASE 'postgres://localhost:5433'")
