from fastapi import FastAPI, HTTPException, Query, Request
import duckdb
import logging
from datetime import datetime
from typing import Optional, List

# Initialize FastAPI app
app = FastAPI()

# Path to the DuckDB database file
DB_PATH = "device.duckdb"  # Ensure this is the correct path to your DuckDB file

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Define a sample API key for verification
API_KEY = "q1LKu7RQyxunnDW"  # Replace with your actual API key if needed

# Endpoint for querying with any field as a filter, including multiple device IDs
@app.get("/query")
async def run_query(
    datetime: Optional[str] = None,
    longitude: Optional[float] = None,
    latitude: Optional[float] = None,
    device_id: Optional[List[int]] = Query(None),
    value: Optional[float] = None,
    unit: Optional[str] = None,
    not_unit: Optional[str] = None,
    height: Optional[float] = None,
    sql: Optional[str] = None
):
    try:
        logging.debug("Connecting to DuckDB")
        conn = duckdb.connect(database=DB_PATH, read_only=True)
        
        # Construct the SQL query based on provided parameters
        if sql:
            # Custom SQL query
            query = sql
            logging.debug(f"Executing custom SQL query: {query}")
        else:
            # Build a dynamic SQL query based on provided fields
            query = "SELECT * FROM measurements"
            filters = []

            if datetime:
                filters.append(f"datetime = '{datetime}'")
            if longitude is not None:
                filters.append(f"longitude = {longitude}")
            if latitude is not None:
                filters.append(f"latitude = {latitude}")
            if device_id:
                # Handle multiple device IDs
                device_ids_str = ", ".join(map(str, device_id))
                filters.append(f"device_id IN ({device_ids_str})")
            if value is not None:
                filters.append(f"value = {value}")
            if unit:
                filters.append(f"unit = '{unit}'")
            if not_unit:
                filters.append(f"unit != '{not_unit}'")
            if height is not None:
                filters.append(f"height = {height}")

            # Add WHERE clause if there are any filters
            if filters:
                query += " WHERE " + " AND ".join(filters)
            
            logging.debug(f"Executing generated query: {query}")

        # Execute the constructed query
        result = conn.execute(query).fetchall()
        column_names = [desc[0] for desc in conn.description]
        conn.close()
        
        # Format the result as JSON
        data = [dict(zip(column_names, row)) for row in result]
        
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
    
    try:
        # Get JSON data from the request
        data = await request.json()
        
        # Add a timestamp if not provided
        data['datetime'] = data.get('datetime', datetime.now().isoformat())

        # Connect to DuckDB and insert the data
        logging.debug("Connecting to DuckDB for insertion")
        conn = duckdb.connect(database=DB_PATH)
        
        # Insert the received data into the measurements table
        conn.execute(
            """
            INSERT INTO measurements (datetime, longitude, latitude, device_id, value, unit, height)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                data['datetime'],
                float(data['longitude']),
                float(data['latitude']),
                int(data['device_id']),
                float(data['value']),
                data['unit'],
                float(data['height']),
            ]
        )
        conn.close()
        
        logging.debug("Data inserted successfully")
        return {"status": "success"}
    
    except Exception as e:
        logging.error(f"Error adding measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Example endpoint for checking if the API is running
@app.get("/status")
async def status():
    return {"status": "API is running"}
