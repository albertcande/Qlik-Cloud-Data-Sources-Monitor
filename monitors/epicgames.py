import requests
from typing import Dict, Any

STATUS_URL = "https://status.epicgames.com/api/v2/status.json"

def check_status() -> Dict[str, Any]:
    """
    Fetches the status of Epic Games service.
    Returns a dictionary with service name, status indicator, and description.
    """
    try:
        response = requests.get(STATUS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        status_data = data.get("status", {})
        indicator = status_data.get("indicator", "unknown")
        description = status_data.get("description", "No description available")
        
        return {
            "service": "Epic Games",
            "status": indicator,
            "message": description
        }
        
    except requests.RequestException as e:
        return {
            "service": "Epic Games",
            "status": "error",
            "message": f"Failed to fetch status: {str(e)}"
        }

if __name__ == "__main__":
    print(check_status())
