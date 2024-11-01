
# Simple Gateway

[![License](https://img.shields.io/github/license/Safecast/simple-gateway)](LICENSE)

The Simple Gateway project serves as a lightweight, HTTP-based endpoint for receiving data from devices and ingesting it into DuckDB. This gateway is designed to process data efficiently for further analysis and storage, making it a key part of device data integration workflows.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **HTTP POST Endpoint**: Receives data directly from devices.
- **DuckDB Integration**: Ingests and stores device data in DuckDB.
- **JSON Handling**: Supports JSON-formatted data for easy device integration.

## Getting Started

### Prerequisites

To run this project, you'll need:

- [DuckDB](https://duckdb.org/) - for data storage.
- [Git](https://git-scm.com/) - for version control.
- [Node.js](https://nodejs.org/) - for running the server.

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Safecast/simple-gateway.git
    cd simple-gateway
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Set up DuckDB and initialize your database as required.

## Usage

To start the server:

```bash
npm start
```

The server will listen for incoming HTTP POST requests to ingest data. You can test it using tools like `curl` or Postman.

### Example Command

```bash
curl -X POST -H "Content-Type: application/json" -d '{"device_urn": "your_device_urn", "data": { ... }}' http://localhost:3000/data
```

## Configuration

Adjust configuration parameters in `.env` or in the `config.js` file to set up database paths, port numbers, and other options.

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
