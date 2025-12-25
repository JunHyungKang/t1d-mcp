import requests
from typing import List, Dict, Any, Optional

class NightscoutClient:
    def __init__(self, url: str, secret: Optional[str] = None):
        """
        Initialize Nightscout Client.
        :param url: Base URL of the Nightscout instance
        :param secret: API Secret (optional, usually needed for write operations or secure instances)
        """
        self.url = url.rstrip('/')
        self.secret = secret

    def get_sgv(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch recent sensor glucose values (SGV).
        Endpoint: /api/v1/entries.json
        """
        headers = {}
        if self.secret:
            # Nightscout usually expects API-SECRET header (SHA1 checksum) or plain in some versions
            # For simplicity in this implementation plan, we assume it passes the token if needed
            # But standard Nightscout auth often uses "api_secret" header
            headers['api-secret'] = self.secret

        params = {'count': count}
        try:
            # Usually Dexcom data is found in /entries.json or /entries/sgv.json
            response = requests.get(f"{self.url}/api/v1/entries.json", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            entries = []
            for entry in data:
                # Filter for valid glucose readings
                if 'sgv' in entry:
                    entries.append({
                        'sgv': entry['sgv'],
                        'direction': entry.get('direction', 'NONE'),
                        'dateString': entry.get('dateString', ''),
                        'delta': entry.get('delta', 0)
                    })
            return entries
        except requests.exceptions.RequestException as e:
            # We catch this in the test
            raise Exception(f"Failed to fetch data from Nightscout: {e}")
