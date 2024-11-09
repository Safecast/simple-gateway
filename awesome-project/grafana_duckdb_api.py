from fastapi import FastAPI, HTTPException, Query, Request
import duckdb
import logging
from datetime import datetime
from typing import Optional, List

app = FastAPI()
DB_PATH = "devices.duckdb"
logging.basicConfig(level=logging.DEBUG)
API_KEY = "q1LKu7RQyxunnDW"

def parse_value(value, data_type):
    try:
        if value == "":
            return None
        return data_type(value)
    except (ValueError, TypeError):
        return None

# Endpoint for querying with any field as a filter, supporting multiple device values and wildcards
@app.get("/query")
async def run_query(
    device: Optional[int] = None,
    bat_voltage: Optional[float] = None,
    dev_temp: Optional[int] = None,
    device_sn: Optional[str] = None,
    device_urn: Optional[str] = None,
    env_temp: Optional[int] = None,
    lnd_7128ec: Optional[float] = None,
    lnd_7318c: Optional[float] = None,
    lnd_7318u: Optional[float] = None,
    loc_country: Optional[str] = None,
    loc_lat: Optional[float] = None,
    loc_lon: Optional[float] = None,
    loc_name: Optional[str] = None,
    pms_pm02_5: Optional[float] = None,
    when_captured: Optional[str] = None
):
    try:
        logging.debug("Connecting to DuckDB")
        conn = duckdb.connect(database=DB_PATH, read_only=True)

        # Check if a device-specific view exists
        table_name = f"device_{device}" if device else "measurements"
        view_exists = conn.execute(
            f"SELECT * FROM information_schema.tables WHERE table_name = '{table_name}'"
        ).fetchone()

        # If the view does not exist, fall back to the main measurements table
        if not view_exists:
            table_name = "measurements"

        query = f"SELECT * FROM {table_name}"
        filters = []

        # Apply filters as needed
        if bat_voltage is not None:
            filters.append(f"bat_voltage = {bat_voltage}")
        if dev_temp is not None:
            filters.append(f"dev_temp = {dev_temp}")
        if device:
            filters.append(f"device = {device}")
        if device_sn:
            filters.append(f"device_sn = '{device_sn}'")
        if device_urn:
            filters.append(f"device_urn = '{device_urn}'")
        if env_temp is not None:
            filters.append(f"env_temp = {env_temp}")
        if lnd_7128ec is not None:
            filters.append(f"lnd_7128ec = {lnd_7128ec}")
        if lnd_7318c is not None:
            filters.append(f"lnd_7318c = {lnd_7318c}")
        if lnd_7318u is not None:
            filters.append(f"lnd_7318u = {lnd_7318u}")
        if loc_country:
            filters.append(f"loc_country = '{loc_country}'")
        if loc_lat is not None:
            filters.append(f"loc_lat = {loc_lat}")
        if loc_lon is not None:
            filters.append(f"loc_lon = {loc_lon}")
        if loc_name:
            filters.append(f"loc_name = '{loc_name}'")
        if pms_pm02_5 is not None:
            filters.append(f"pms_pm02_5 = {pms_pm02_5}")
        if when_captured:
            filters.append(f"when_captured = '{when_captured}'")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        logging.debug(f"Executing generated query: {query}")

        result = conn.execute(query).fetchall()
        column_names = [desc[0] for desc in conn.description]
        conn.close()

        data = [{col: val for col, val in zip(column_names, row)} for row in result]

        logging.debug("Query executed successfully")
        return {"data": data}
    
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for inserting data into the "measurements" table
@app.post("/measurements")
async def add_measurement(request: Request, api_key: str = Query(...)):
    # Verify the API key
    if api_key != API_KEY:
        logging.warning("Unauthorized attempt with invalid API key")
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Get JSON data from the request
    data = await request.json()
    
    # Add a timestamp if not provided
    data['when_captured'] = data.get('when_captured', datetime.now().isoformat())
    data['received_at'] = datetime.now().isoformat()  # Capture the time the data is received

    # Prepare the data for insertion, converting empty strings to None
    cleaned_data = {
        "bat_voltage": parse_value(data.get("bat_voltage"), float),
        "dev_temp": parse_value(data.get("dev_temp"), int),
        "device": parse_value(data.get("device"), int),
        "device_sn": data.get("device_sn"),
        "device_urn": data.get("device_urn"),
        "env_temp": parse_value(data.get("env_temp"), int),
        "lnd_7128ec": parse_value(data.get("lnd_7128ec"), float),
        "lnd_7318c": parse_value(data.get("lnd_7318c"), float),
        "lnd_7318u": parse_value(data.get("lnd_7318u"), float),
        "loc_country": data.get("loc_country"),
        "loc_lat": parse_value(data.get("loc_lat"), float),
        "loc_lon": parse_value(data.get("loc_lon"), float),
        "loc_name": data.get("loc_name"),
        "pms_pm02_5": parse_value(data.get("pms_pm02_5"), float),
        "when_captured": data["when_captured"],
        "received_at": data["received_at"],
        # Capture additional fields directly
        **{key: value for key, value in data.items() if key not in {
            "bat_voltage", "dev_temp", "device", "device_sn", "device_urn",
            "env_temp", "lnd_7128ec", "lnd_7318c", "lnd_7318u", "loc_country",
            "loc_lat", "loc_lon", "loc_name", "pms_pm02_5", "when_captured", "received_at"
        }}
    }

    # Check for new fields in the data and add them if needed
    with duckdb.connect(DB_PATH) as conn:
        existing_columns = {row[0] for row in conn.execute("PRAGMA table_info(measurements)").fetchall()}
        
        # Dynamically add any new fields not already in the table
        for field, value in cleaned_data.items():
            if field not in existing_columns:
                column_type = "DOUBLE" if isinstance(value, (int, float)) else "VARCHAR"
                logging.debug(f"Adding new column '{field}' of type '{column_type}'")
                try:
                    conn.execute(f"ALTER TABLE measurements ADD COLUMN {field} {column_type}")
                except duckdb.CatalogException:
                    logging.debug(f"Column '{field}' already exists.")
                existing_columns.add(field)

    # Insert data, allowing for duplicates based on received_at
    conn = duckdb.connect(database=DB_PATH)
    try:
        columns = ", ".join(cleaned_data.keys())
        placeholders = ", ".join(["?" for _ in cleaned_data])
        values = [cleaned_data.get(col, None) for col in cleaned_data]

        conn.execute(
            f"INSERT INTO measurements ({columns}) VALUES ({placeholders})", values
        )
        logging.debug("Data inserted successfully")

        conn.close()
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error adding measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Example endpoint for checking if the API is running
@app.get("/status")
async def status():
    return {"status": "API is running"}
