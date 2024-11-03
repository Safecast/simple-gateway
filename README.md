# **Simple Gateway for Measurements API**

This project provides an API to insert and query measurement data in a DuckDB database. The API is built with FastAPI and supports data ingestion, custom SQL querying, and flexible data filtering for use with monitoring tools like Grafana.

## **Requirements**

* **DuckDB**: Ensure DuckDB is installed and accessible.  
* **Python**: Requires Python 3.7+ and `fastapi`, `uvicorn`, and `duckdb` libraries.  
  Install dependencies:  
  bash

`pip install fastapi uvicorn duckdb`

* 

## **Setup**

1. Clone the repository and navigate to the project directory.  
2. Initialize a DuckDB database file named `devices.duckdb`:  
   bash

`duckdb devices.duckdb`

Create the main `measurements` table within DuckDB:  
sql  
`CREATE TABLE measurements (`  
    `bat_voltage DOUBLE,`  
    `dev_temp INTEGER,`  
    `device BIGINT,`  
    `device_sn VARCHAR,`  
    `device_urn VARCHAR,`  
    `env_temp INTEGER,`  
    `lnd_7128ec DOUBLE,`  
    `lnd_7318c DOUBLE,`  
    `lnd_7318u DOUBLE,`  
    `loc_country VARCHAR,`  
    `loc_lat DOUBLE,`  
    `loc_lon DOUBLE,`  
    `loc_name VARCHAR,`  
    `pms_pm02_5 DOUBLE,`  
    `when_captured TIMESTAMP,`  
    `received_at TIMESTAMP`  
`);`

1. 

## **Running the API**

To start the FastAPI server:

bash  
`uvicorn grafana_duckdb_api:app --host 0.0.0.0 --port 8000`

Or, for production use, start with Gunicorn and Uvicorn workers:

bash  
`gunicorn -w 4 -k uvicorn.workers.UvicornWorker grafana_duckdb_api:app --bind 0.0.0.0:8000`

## **API Endpoints**

### **POST `/measurements`**

Ingest a new measurement into the DuckDB database.

* **Parameters**:  
  * `api_key` (required): A sample API key `q1LKu7RQyxunnDW` is used for testing purposes. Replace it as needed.  
  * **Payload**: JSON with fields such as `bat_voltage`, `dev_temp`, `device`, etc. Empty string values are automatically converted to `NULL` by the API.  
* **Example**:  
  bash

`curl -X POST "http://localhost:8000/measurements?api_key=q1LKu7RQyxunnDW" \`  
     `-H "Content-Type: application/json" \`  
     `-d '{`  
         `"bat_voltage": "3.7",`  
         `"dev_temp": "25",`  
         `"device": "2830364905",`  
         `"device_sn": "SN12345",`  
         `"device_urn": "urn:dev:12345",`  
         `"env_temp": "30",`  
         `"lnd_7128ec": "60",`  
         `"lnd_7318c": "",`  
         `"lnd_7318u": "20",`  
         `"loc_country": "US",`  
         `"loc_lat": "37.7749",`  
         `"loc_lon": "-122.4194",`  
         `"loc_name": "San Francisco",`  
         `"pms_pm02_5": "12.5",`  
         `"when_captured": "2024-11-02T15:30:00"`  
     `}'`

* 

### **GET `/query`**

Fetch data based on query filters for any of the supported fields. Useful for Grafana integration.

* **Parameters**: Any field from the `measurements` table can be used as a filter, e.g., `device`, `device_sn`, `when_captured`, etc. Multiple `device` values can be specified with `device=123&device=456`.  
* **Example**:  
  bash

`curl -X GET "http://localhost:8000/query?device_sn=SN12345"`

**Example for Multiple Devices**:  
bash  
`curl -X GET "http://localhost:8000/query?device=123&device=456"`

* 

### **GET `/status`**

A simple health check to verify that the API is running.

## **Notes**

* **Dynamic Column Addition**: The API automatically adds any new columns to the `measurements` table if new fields are received in the JSON payload.  
* **Handling Nulls**: Empty string values are converted to `NULL` before insertion into DuckDB, ensuring data integrity and allowing accurate querying.

## **Grafana Integration**

For Grafana, use the **Infinity** datasource to connect to the API:

1. Set up a **Yesoreyeram Infinity** datasource.  
2. Set the **URL** to `http://localhost:8000/query` and specify query parameters using JSONPath or direct query fields.  
3. Configure queries as needed for custom visualization.

