import duckdb

# Connect to DuckDB (this will create devices.duckdb if it doesn't exist)
conn = duckdb.connect('devices.duckdb')

# Create a measurements table
conn.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
        datetime TIMESTAMP,
        longitude DOUBLE,
        latitude DOUBLE,
        device_id VARCHAR,
        value DOUBLE,
        unit VARCHAR,
        height DOUBLE
    )
''')


