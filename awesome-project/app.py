from fastapi import FastAPI, Request, HTTPException
import duckdb
from datetime import datetime

app = FastAPI()

@app.post("/measurements")
async def receive_measurement(request: Request):
    try:
        with duckdb.connect('devices.duckdb') as db_connection:
            data = await request.json()
            data['datetime'] = data.get('datetime', datetime.now().isoformat())

            db_connection.execute('''
                INSERT INTO measurements (datetime, longitude, latitude, device_id, value, unit, height)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [data['datetime'], float(data['longitude']), float(data['latitude']),
                  data['device_id'], float(data['value']), data['unit'], float(data['height'])])

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
