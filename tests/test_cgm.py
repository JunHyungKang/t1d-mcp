import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cgm.nightscout import NightscoutClient
from cgm.dexcom import DexcomClient

class TestNightscout(unittest.TestCase):
    def setUp(self):
        self.url = "https://my-nightscout.herokuapp.com"
        self.client = NightscoutClient(self.url)

    @patch('requests.get')
    def test_fetch_sgv_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "sgv": 150, "direction": "Flat", "dateString": "2025-12-25T15:00:00.000Z", "delta": 2
        }]
        mock_get.return_value = mock_response

        entries = self.client.get_sgv(count=1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['sgv'], 150)

class TestDexcom(unittest.TestCase):
    def setUp(self):
        self.client = DexcomClient("user", "pass")

    @patch('cgm.dexcom.Dexcom')
    def test_get_latest_glucose_success(self, mock_dexcom_cls):
        # Mock Dexcom instance and return value
        mock_instance = mock_dexcom_cls.return_value
        
        # Mock GlucoseReading object
        mock_reading = MagicMock()
        mock_reading.value = 120
        mock_reading.trend_description = "flat"
        mock_reading.trend_arrow = "→"
        mock_reading.datetime = datetime(2025, 12, 25, 12, 0, 0)
        mock_reading.trend_direction = 1
        
        mock_instance.get_current_glucose_reading.return_value = mock_reading
        
        result = self.client.get_latest_glucose()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['sgv'], 120)
        self.assertEqual(result['direction'], "flat")
        self.assertEqual(result['time'], "2025-12-25 12:00:00")

if __name__ == '__main__':
    unittest.main()
