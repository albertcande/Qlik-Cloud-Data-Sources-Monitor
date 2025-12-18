# Data Sources Monitor
A lightweight Python application that monitors the health status of external services like Snowflake, MongoDB, GitHub... and automatically updates a Qlik Cloud tenant banner to reflect any incidents or outages in real-time.

## Features

- **Multi-Service Monitoring**: Polls status pages from Snowflake, MongoDB, GitHub, and Epic Games every 60 seconds.
- **Automatic Banner Updates**: Upserts a Qlik Cloud announcement banner via the REST API when issues are detected.
- **Severity Mapping**: Maps external status indicators (`major`, `minor`, `critical`, `maintenance`) to Qlik banner types (`error`, `warning`, `info`).
- **Auto-Clear**: Automatically clears the banner when all services return to normal.
- **Logging**: Outputs to both console and a local `monitor.log` file for easy debugging.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py (Orchestrator)                  │
│  - Runs polling loop every 60s                                  │
│  - Aggregates status from all monitors                          │
│  - Determines highest severity                                  │
│  - Calls Qlik API to update banner                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │  snowflake.py │ │  mongodb.py   │ │  github.py    │ ...
   │  (Monitor)    │ │  (Monitor)    │ │  (Monitor)    │
   └───────────────┘ └───────────────┘ └───────────────┘
           │               │               │
           ▼               ▼               ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                  StatusPage APIs (/api/v2/status.json)      │
   └─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- A Qlik Cloud tenant with API access
- A Qlik Cloud API key with permissions to manage banners

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/albertcande/Qlik-Cloud-Data-Sources-Monitor.git
   cd qlik-cloud-data-sources-monitor
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy the example file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   QLIK_TENANT_URL=https://your-tenant.region.qlikcloud.com
   QLIK_API_KEY=your-api-key-here
   ```

## Usage

Run the monitor:
```bash
python main.py
```

The application will:
1. Poll all configured status pages every 60 seconds.
2. Log the results to the console and `monitor.log`.
3. Update the Qlik Cloud banner if any service reports an issue.
4. Clear the banner when all services are operational.

### Example Output

```
2025-12-18 12:05:03 - MainOrchestrator - INFO - Starting Qlik Cloud Data Sources Monitor...
2025-12-18 12:05:03 - MainOrchestrator - INFO - Checking services status...
2025-12-18 12:05:04 - MainOrchestrator - WARNING - Issues detected: Epic Games: Service Under Maintenance (Severity: minor)
2025-12-18 12:05:04 - QlikClient - INFO - API Response: {"id":"...","enabled":true,"type":"warning",...}
2025-12-18 12:05:04 - MainOrchestrator - INFO - Banner updated successfully.
```

## Adding New Monitors

To add a new service to monitor:

1. Create a new file in `monitors/`, e.g., `monitors/newservice.py`:
   ```python
   import requests
   from typing import Dict, Any

   STATUS_URL = "https://status.newservice.com/api/v2/status.json"

   def check_status() -> Dict[str, Any]:
       try:
           response = requests.get(STATUS_URL, timeout=10)
           response.raise_for_status()
           data = response.json()
           status_data = data.get("status", {})
           return {
               "service": "NewService",
               "status": status_data.get("indicator", "unknown"),
               "message": status_data.get("description", "No description")
           }
       except requests.RequestException as e:
           return {"service": "NewService", "status": "error", "message": str(e)}
   ```

2. Import and call it in `monitors/health.py`:
   ```python
   from .newservice import check_status as check_newservice
   # ...
   results.append(check_newservice())
   ```

## Project Structure

```
mvp-qlik-monitor/
├── main.py              # Main orchestrator loop
├── qlik_client.py       # Qlik Cloud API client (banner upsert)
├── monitors/
│   ├── __init__.py
│   ├── health.py        # Aggregates all service checks
│   ├── snowflake.py     # Snowflake status monitor
│   ├── mongodb.py       # MongoDB status monitor
│   ├── github.py        # GitHub status monitor
│   └── epicgames.py     # Epic Games status monitor
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md            # This file
```

## Technologies Used

- **Python 3.12**
- **Requests** - HTTP client for API calls
- **python-dotenv** - Environment variable management
- **Qlik Cloud REST API** - Banner management

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
