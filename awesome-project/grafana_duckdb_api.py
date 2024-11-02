from fastapi import FastAPI
import duckdb
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
DB_PATH = "/home/rob/Documents/simple-gateway/awesome-project/devices.duckdb"  # Ensure this is the correct path

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
        return {"status": "error", "message": str(e)}