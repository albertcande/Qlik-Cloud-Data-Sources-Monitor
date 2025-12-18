import os
import subprocess
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def upsert_banner(status_type: str, message: str, enabled: bool = True) -> Dict[str, Any]:
    """
    Upserts the tenant banner configuration.
    
    Args:
        status_type: One of 'major', 'minor', 'none', 'critical' (from StatusPage)
        message: The text to display
        enabled: Whether the banner should be visible
    
    Returns:
        JSON response from the API
    """
    # Lazy load env vars to ensure they are available if set after import
    tenant_url = os.getenv("QLIK_TENANT_URL")
    api_key = os.getenv("QLIK_API_KEY")

    if not tenant_url:
        # Try loading dotenv again just in case
        load_dotenv()
        tenant_url = os.getenv("QLIK_TENANT_URL")
        api_key = os.getenv("QLIK_API_KEY")

    if not tenant_url:
        raise ValueError("QLIK_TENANT_URL is not set in environment variables. Please check your .env file.")
    
    if not api_key:
        raise ValueError("QLIK_API_KEY is not set in environment variables. Please check your .env file.")

    endpoint = f"{tenant_url}/api/v1/banners/actions/upsert"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Map StatusPage indicators to Qlik Banner types
    # Qlik supports: 'info', 'warning', 'error' (inferred from example and standard practices)
    severity_map = {
        'major': 'error',
        'critical': 'error',
        'minor': 'warning',
        'maintenance': 'warning',
        'none': 'info',
        'unknown': 'info'
    }
    
    # "type" field determines the color/icon of the banner
    banner_type = severity_map.get(status_type.lower(), 'info')
    
    # Qlik API requires startTime, endTime and linkEnabled
    # We use UTC for consistency
    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    end_time = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    payload = {
        "message": message,
        "type": banner_type,
        "enabled": enabled,
        "startTime": start_time,
        "endTime": end_time,
        "linkEnabled": False
    }
    
    json_payload = json.dumps(payload)
    
    # Executing cURL via subprocess as requested
    curl_command = [
        "curl",
        endpoint,
        "-X", "POST",
        "-H", "Content-type: application/json",
        "-H", f"Authorization: Bearer {api_key}",
        "-d", json_payload
    ]
    
    try:
        # Capture output for debugging and response parsing
        # Use -s to avoid progress bar in capture
        curl_command.insert(1, "-s") 
        
        result = subprocess.run(
            curl_command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Log the response for debugging purposes
        import logging
        logger = logging.getLogger("QlikClient")
        logger.info(f"API Response: {result.stdout}")
        if result.stderr:
            logger.warning(f"API Stderr: {result.stderr}")
        
        # Try to return JSON if possible, else the raw stdout
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"output": result.stdout}
            
    except subprocess.CalledProcessError as e:
        import logging
        logger = logging.getLogger("QlikClient")
        logger.error(f"Error executing cURL: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}")
        raise

if __name__ == "__main__":
    # Test execution (will fail without real creds, but verifies import/structure)
    try:
        print("Attempting to run clean run...")
        # Simulating a 'none' status which might disable it or set to info
        # upsert_banner("none", "Systems Operational", enabled=False) 
        print("Client module loaded.")
    except Exception as e:
        print(f"Test run failed: {e}")
