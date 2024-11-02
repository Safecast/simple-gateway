from fastapi import FastAPI, HTTPException
import duckdb
from datetime import datetime

app = FastAPI()

# Other endpoints...

@app.post("/annotations")
async def annotations(request: dict):
    return []
