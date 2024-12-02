import duckdb

# Connect to your DuckDB database
conn = duckdb.connect('devices.duckdb')

# Specify the captured_at value
captured_at_value = '2024-11-02T15:47:00'

# Query to fetch rows where captured_at matches the specified value
result = conn.execute("SELECT * FROM measurements WHERE when_captured = ?", [captured_at_value]).fetchall()

# Print the result
for row in result:
    print(row)

conn.close()

