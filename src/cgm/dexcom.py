from pydexcom import Dexcom
from typing import List, Dict, Any, Optional

class DexcomClient:
    def __init__(self, username: str, password: str, region: str = "US"):
        """
        Initialize Dexcom Client.
        :param username: Dexcom Share Username
        :param password: Dexcom Share Password
        :param region: 'US' or 'OUS' (Outside US, e.g., Korea uses OUS often but sometimes US depending on account creation)
        """
        self.username = username
        self.password = password
        self.region = region

    def get_latest_glucose(self) -> Optional[Dict[str, Any]]:
        try:
            # pydexcom requires login
            dexcom = Dexcom(self.username, self.password, ous=(self.region == "OUS"))
            
            # Get current reading
            bg = dexcom.get_current_glucose_reading()
            if not bg:
                return None
            
            return {
                "sgv": bg.value,
                "direction": bg.trend_description, # pydexcom returns string like 'flat', 'singleUp'
                "trend_arrow": bg.trend_arrow,     # Unicode arrow usually
                "time": bg.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "delta": bg.trend_direction        # Sometimes rough estimate, but pydexcom provides value diff? 
                                                   # Actually pydexcom object has .trend (int) and .value (mg/dL)
                                                   # We might need to fetch history to calc delta accurately if not provided
            }
        except Exception as e:
            raise Exception(f"Dexcom Login/Fetch Failed: {e}")

    def get_readings(self, minutes: int = 1440, max_count: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch recent history
        """
        try:
            dexcom = Dexcom(self.username, self.password, ous=(self.region == "OUS"))
            # readings method
            # pydexcom APIs: get_glucose_readings(minutes=...)
            readings = dexcom.get_glucose_readings(minutes=minutes, max_count=max_count)
            
            result = []
            for r in readings:
                result.append({
                    "sgv": r.value,
                    "direction": r.trend_description,
                    "time": r.datetime.strftime("%H:%M"),
                    "delta": 0 # TODO: Calculate delta from previous
                })
            return result
        except Exception as e:
            raise Exception(f"Dexcom History Failed: {e}")
