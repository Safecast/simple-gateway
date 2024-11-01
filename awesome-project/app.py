from fastapi import FastAPI, Request, HTTPException
import duckdb
from datetime import datetime

app = FastAPI()

@app.post("/measurements")
async def receive_measurement(request: Request):
    try:
        # Open a new connection for each request
        with duckdb.connect('devices.duckdb') as db_connection:
            # Parse incoming JSON data
            data = await request.json()
            
            # Convert timestamp if not provided
            data['datetime'] = data.get('datetime', datetime.now().isoformat())

            # Insert data into DuckDB
            db_connection.execute('''
                INSERT INTO measurements (datetime, longitude, latitude, device_id, value, unit, height)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [data['datetime'], float(data['longitude']), float(data['latitude']), 
                  data['device_id'], float(data['value']), data['unit'], float(data['height'])])

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))