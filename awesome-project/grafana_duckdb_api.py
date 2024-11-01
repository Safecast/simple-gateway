from fastapi import FastAPI, HTTPException
import duckdb
from datetime import datetime

app = FastAPI()

@app.get("/search")
async def search():
    # Return the available fields as a list
    return ["value", "longitude", "latitude", "height"]

@app.post("/query")
async def query(request: dict):
    target = request["targets"][0]["target"]
    
    # Open a new DuckDB connection within this request
    try:
        with duckdb.connect('devices.duckdb') as db_connection:
            data = db_connection.execute(f'''
                SELECT datetime, {target} FROM measurements ORDER BY datetime
            ''').fetchall()

            # Format the data in a way Grafana can read
            return [{
                "target": target,
                "datapoints": [
                    [row[1], int(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)]
                    for row in data
                ]
            }]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/annotations")
async def annotations(request: dict):
    return []
