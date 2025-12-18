import time
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import our modules
from monitors.health import check_all_services
from qlik_client import upsert_banner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("monitor.log")
    ]
)
logger = logging.getLogger("MainOrchestrator")

def format_banner_message(issues: List[Dict[str, Any]]) -> str:
    """
    Creates a user-friendly message from a list of issues.
    """
    if not issues:
        return ""
    
    messages = []
    for issue in issues:
        service = issue.get("service")
        msg = issue.get("message")
        messages.append(f"{service}: {msg}")
    
    return " | ".join(messages)

def determine_severity(issues: List[Dict[str, Any]]) -> str:
    """
    Determines the highest severity from a list of issues.
    Hierarchy: critical > major > minor > maintenance > none
    """
    severity_rank = {
        'critical': 5,
        'major': 4,
        'error': 4,
        'minor': 3,
        'warning': 3,
        'maintenance': 2,
        'none': 1,
        'unknown': 0
    }
    
    max_severity = 'none'
    max_rank = 0
    
    for issue in issues:
        status = issue.get("status", "none").lower()
        rank = severity_rank.get(status, 0)
        if rank > max_rank:
            max_rank = rank
            max_severity = status
            
    return max_severity

def main_loop():
    load_dotenv()
    logger.info("Starting Data Sources Status Monitor...")
    
    poll_interval = 60 # Check every 60 seconds as per goal "under 60 seconds"
    # Task 3 says "loop every 5 minutes", but Goal says "under 60 seconds".
    # I'll stick to 60s for the MVP to demonstrate the speed.
    
    while True:
        try:
            logger.info("Checking services status...")
            results = check_all_services()
            
            issues = []
            for res in results:
                # We consider anything not 'none' as an issue worth reporting
                # StatusPage usually uses 'none' for 'All System Operational'
                if res.get("status", "").lower() != "none":
                    issues.append(res)
            
            if issues:
                severity = determine_severity(issues)
                message = format_banner_message(issues)
                logger.warning(f"Issues detected: {message} (Severity: {severity})")
                
                # Upsert banner
                # We map severity to qlik types in logic above or pass raw status
                # Here we pass the raw status of the worst issue
                upsert_banner(severity, message, enabled=True)
                logger.info("Banner updated successfully.")
            else:
                logger.info("All services operational. Clearing banner.")
                # Clear/Disable banner
                upsert_banner("none", "All Systems Operational", enabled=False)
                
        except Exception as e:
            logger.error(f"An error occurred in the main loop: {e}", exc_info=True)
        
        time.sleep(poll_interval)

if __name__ == "__main__":
    main_loop()

