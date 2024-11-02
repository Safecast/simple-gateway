from fastapi import FastAPI, HTTPException, Request
import duckdb
import threading
import logging
from datetime import datetime

# Configuration
DB_PATH = "/home/rob/Documents/simple-gateway/awesome-project/devices.duckdb"  # Update this path
POSTGRES_PORT = 5433

# Initialize FastAPI
app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Start DuckDB in server mode in a separate thread
def start_duckdb_server():
    duckdb.connect(database=DB_PATH).execute(f"INSTALL postgres_scanner; LOAD postgres_scanner;")
    duckdb.connect(database=DB_PATH).execute(f"EXPORT DATABASE 'postgres://localhost:{POSTGRES_PORT}'")

duckdb_thread = threading.Thread(target=start_duckdb_server, daemon=True)
duckdb_thread.start()

# FastAPI endpoints
@app.get("/measurements")
async def get_measurements():
    try:
        conn = duckdb.connect(database=DB_PATH, read_only=True)
        query = "SELECT datetime, longitude, latitude, device_id, value, unit, height FROM measurements"
        results = conn.execute(query).fetchall()
        data = [
            {
                "datetime": row[0],
                "longitude": row[1],
                "latitude": row[2],
                "device_id": row[3],
                "value": row[4],
                "unit": row[5],
                "height": row[6]
            }
            for row in results
        ]
        return data
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/measurements")
async def add_measurement(request: Request):
    try:
        data = await request.json()  # Parse incoming JSON data
        data['datetime'] = data.get('datetime', datetime.now().isoformat())

        with duckdb.connect(database=DB_PATH, read_only=False) as conn:
            conn.execute('''
                INSERT INTO measurements (datetime, longitude, latitude, device_id, value, unit, height)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [
                data['datetime'],
                float(data['longitude']),
                float(data['latitude']),
                data['device_id'],
                float(data['value']),
                data['unit'],
                float(data['height'])
            ])

        return {"status": "success", "message": "Data added successfully"}

    except Exception as e:
        logger.error(f"Error adding data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
