from fastapi import FastAPI, HTTPException, Query, Request
import duckdb
import logging
from datetime import datetime
from typing import Optional

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

# Endpoint to retrieve distinct values for a column
@app.get("/distinct")
async def get_distinct_values(column: str):
    """
    Retrieve all unique values from a specified column in the measurements table,
    formatted as JSON with field-value pairs.
    """
    try:
        logging.debug(f"Fetching distinct values for column: {column}")

        # Connect to the database
        conn = duckdb.connect(database=DB_PATH, read_only=True)

        # Fetch valid column names
        valid_columns = {row[1].lower() for row in conn.execute("PRAGMA table_info(measurements)").fetchall()}
        logging.debug(f"Valid columns: {valid_columns}")

        # Validate the requested column
        if column.lower() not in valid_columns:
            raise HTTPException(status_code=400, detail=f"Invalid column name: {column}")

        # Query for distinct values
        query = f"SELECT DISTINCT {column} FROM measurements"
        logging.debug(f"Executing query: {query}")
        result = conn.execute(query).fetchall()
        conn.close()

        # Format the result as a list of JSON objects
        formatted_result = [{column: row[0]} for row in result]

        logging.debug("Distinct values retrieved successfully")
        return {"data": formatted_result}

    except Exception as e:
        logging.error(f"Error retrieving distinct values: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced /query endpoint
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
    when_captured: Optional[str] = None,
    start_time: Optional[str] = None,  # New start time filter
    end_time: Optional[str] = None,    # New end time filter
):
    """
    Run a dynamic query on the measurements table with optional filters and time range.
    """
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
        if start_time:
            filters.append(f"when_captured >= '{start_time}'")
        if end_time:
            filters.append(f"when_captured <= '{end_time}'")

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

# Endpoint for inserting data into the measurements table
@app.post("/measurements")
async def add_measurement(request: Request, api_key: str = Query(...)):
    if api_key != API_KEY:
        logging.warning("Unauthorized access attempt")
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        data = await request.json()
        data['when_captured'] = data.get('when_captured', datetime.now().isoformat())
        data['received_at'] = datetime.now().isoformat()

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
        }

        with duckdb.connect(DB_PATH) as conn:
            existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(measurements)").fetchall()}
            for field, value in cleaned_data.items():
                if field not in existing_columns:
                    column_type = "DOUBLE" if isinstance(value, (int, float)) else "VARCHAR"
                    conn.execute(f"ALTER TABLE measurements ADD COLUMN {field} {column_type}")

            columns = ", ".join(cleaned_data.keys())
            placeholders = ", ".join(["?" for _ in cleaned_data])
            values = [cleaned_data.get(col) for col in cleaned_data]

            conn.execute(f"INSERT INTO measurements ({columns}) VALUES ({placeholders})", values)
        logging.debug("Data inserted successfully")
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error adding measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to check API status
@app.get("/status")
async def status():
    return {"status": "API is running"}
