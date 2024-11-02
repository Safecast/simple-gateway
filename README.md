# **Simple Gateway with DuckDB API**

This project is a simple data ingestion and querying gateway using FastAPI, DuckDB, and Grafana. It allows devices to send data to a DuckDB database and provides endpoints for querying the data. This setup also supports integration with Grafana via the Yesoreyeram Infinity data source for visualizations.

## **Features**

* **Data Ingestion**: Devices can send JSON data to the `/measurements` endpoint.  
* **Flexible Querying**: The `/query` endpoint allows for SQL-like querying with dynamic filtering options for various fields in the `measurements` table.  
* **Grafana Integration**: Integrates with Grafana using the Infinity plugin, enabling data visualization with SQL-like flexibility.

## **Requirements**

* Python 3.7+  
* FastAPI  
* DuckDB  
* Gunicorn (for production deployment)  
* Uvicorn (for running FastAPI with Gunicorn)

## **Setup**

1. Clone the repository:  
   bash

`git clone https://github.com/Safecast/simple-gateway.git`  
`cd simple-gateway`

Install dependencies:  
bash  
`python3 -m venv .venv`  
`source .venv/bin/activate`  
`pip install -r requirements.txt`

Create or update your DuckDB database:

* Ensure that `device.duckdb` exists in your project directory and contains the `measurements` table.  
* The table structure should be as follows:

sql  
`CREATE TABLE measurements (`  
    `datetime TIMESTAMP,`  
    `longitude DOUBLE,`  
    `latitude DOUBLE,`  
    `device_id INTEGER,`  
    `value DOUBLE,`  
    `unit VARCHAR,`  
    `height DOUBLE`  
`);`

1. 

## **Running the Application**

For development, you can run the FastAPI application with Uvicorn:

bash  
`uvicorn grafana_duckdb_api:app --reload`

For production, use Gunicorn with Uvicorn workers:

bash  
`gunicorn -w 4 -k uvicorn.workers.UvicornWorker grafana_duckdb_api:app --bind 0.0.0.0:8000`

## **Endpoints**

### **1\. `/measurements` (POST)**

Ingest data into the `measurements` table.

* **Method**: `POST`  
* **Query Parameter**: `api_key` (required)  
* **Body**: JSON with the following fields:  
  * `longitude` (float)  
  * `latitude` (float)  
  * `device_id` (integer)  
  * `value` (float)  
  * `unit` (string)  
  * `height` (float)  
  * `datetime` (optional, ISO 8601 format; if omitted, the server time will be used)

**Example**:

bash  
`curl -X POST "http://localhost:8000/measurements?api_key=q1LKu7RQyxunnDW" \`  
     `-H "Content-Type: application/json" \`  
     `-d '{`  
            `"longitude": 139.7449,`  
            `"latitude": 35.6617,`  
            `"device_id": 47,`  
            `"value": 40,`  
            `"unit": "cpm",`  
            `"height": 111`  
         `}'`

### **2\. `/query` (GET)**

Query data from the `measurements` table. Supports flexible filtering by multiple fields and custom SQL queries.

* **Method**: `GET`  
* **Query Parameters** (all optional):  
  * `datetime`: ISO 8601 timestamp to filter by specific datetime.  
  * `longitude`: Filter by longitude.  
  * `latitude`: Filter by latitude.  
  * `device_id`: Filter by one or more device IDs (e.g., `device_id=47&device_id=49`).  
  * `value`: Filter by value.  
  * `unit`: Filter by unit (e.g., `"cpm"`).  
  * `not_unit`: Exclude a specific unit (e.g., `not_unit=cpm`).  
  * `height`: Filter by height.  
  * `sql`: Custom SQL query (overrides other filters).

**Examples**:

1. **Query by `device_id` and `height`**:  
   bash

`curl "http://localhost:8000/query?device_id=47&height=111.0"`

**Query by Multiple `device_id`s**:  
bash  
`curl "http://localhost:8000/query?device_id=47&device_id=49"`

**Query by `unit != cpm`**:  
bash  
`curl "http://localhost:8000/query?not_unit=cpm"`

**Custom SQL Query**:  
bash  
`curl "http://localhost:8000/query?sql=SELECT%20*%20FROM%20measurements%20WHERE%20value%20%3E%2010"`

1. 

### **3\. `/status` (GET)**

Check if the API is running.

* **Method**: `GET`

**Example**:

bash  
`curl http://localhost:8000/status`

## **Grafana Integration**

This setup works well with the Grafana **Infinity** plugin to visualize data.

1. **Install the Infinity Plugin**:  
   bash

`grafana-cli plugins install yesoreyeram-infinity-datasource`  
`sudo systemctl restart grafana-server`

1.   
2. **Configure the Data Source in Grafana**:  
   * Go to **Configuration \> Data Sources** in Grafana.  
   * Add **Infinity** as a new data source.  
   * Set **Source** to `URL` and use URLs like the examples provided in `/query` endpoint documentation.  
3. **Using Queries in Grafana Panels**:  
   * Query data by constructing URLs with the desired filters. For example:  
     * `http://localhost:8000/query?device_id=47`  
     * `http://localhost:8000/query?not_unit=cpm`

This setup allows you to filter data flexibly in Grafana using both standard filters and custom SQL, making it easy to visualize measurements stored in DuckDB.

