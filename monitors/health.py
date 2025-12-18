from typing import List, Dict, Any
from .snowflake import check_status as check_snowflake
from .mongodb import check_status as check_mongodb
from .github import check_status as check_github
from .epicgames import check_status as check_epicgames

def check_all_services() -> List[Dict[str, Any]]:
    """
    Checks status for all configured services.
    Returns a list of status dictionaries.
    """
    results = []
    
    # Check Snowflake
    results.append(check_snowflake())
    
    # Check MongoDB
    results.append(check_mongodb())
    
    # Check GitHub
    results.append(check_github())

    # Check Epic Games
    results.append(check_epicgames())
    
    return results

if __name__ == "__main__":
    import json
    print(json.dumps(check_all_services(), indent=2))
