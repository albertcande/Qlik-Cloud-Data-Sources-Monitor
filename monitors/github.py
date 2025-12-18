import requests
from typing import Dict, Any

STATUS_URL = "https://www.githubstatus.com/api/v2/status.json"

def check_status() -> Dict[str, Any]:
    """
    Fetches the status of GitHub service.
    Returns a dictionary with service name, status indicator, and description.
    """
    try:
        # GitHub uses Atlassian Statuspage, same as Snowflake/MongoDB
        response = requests.get(STATUS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        status_data = data.get("status", {})
        indicator = status_data.get("indicator", "unknown")
        description = status_data.get("description", "No description available")
        
        return {
            "service": "GitHub",
            "status": indicator,
            "message": description
        }
        
    except requests.RequestException as e:
        return {
            "service": "GitHub",
            "status": "error",
            "message": f"Failed to fetch status: {str(e)}"
        }

if __name__ == "__main__":
    print(check_status())
