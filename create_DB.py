import duckdb

# Connect to DuckDB (this will create devices.duckdb if it doesn't exist)
conn = duckdb.connect('devices.duckdb')

# Create a measurements table
conn.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
    bat_voltage DOUBLE,
    dev_temp INTEGER,
    device BIGINT,
    device_sn VARCHAR,
    device_urn VARCHAR,
    env_temp INTEGER,
    lnd_7128ec DOUBLE,
    lnd_7318c DOUBLE,
    lnd_7318u DOUBLE,
    loc_country VARCHAR,
    loc_lat DOUBLE,
    loc_lon DOUBLE,
    loc_name VARCHAR,
    pms_pm02_5 DOUBLE,
    when_captured TIMESTAMP
    )
''')


