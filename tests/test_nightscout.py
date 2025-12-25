import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cgm.nightscout import NightscoutClient

class TestNightscout(unittest.TestCase):
    def setUp(self):
        self.url = "https://my-nightscout.herokuapp.com"
        self.client = NightscoutClient(self.url)

    @patch('requests.get')
    def test_fetch_sgv_success(self, mock_get):
        # Mock successful response from Nightscout API (entries.json)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "sgv": 150,
                "direction": "Flat",
                "dateString": "2025-12-25T15:00:00.000Z",
                "delta": 2
            }
        ]
        mock_get.return_value = mock_response

        # Call the method
        entries = self.client.get_sgv(count=1)

        # Assertions
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['sgv'], 150)
        self.assertEqual(entries[0]['direction'], "Flat")

    @patch('requests.get')
    def test_fetch_sgv_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401 # Unauthorized
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_get.return_value = mock_response

        # Call method and expect exception
        with self.assertRaises(Exception):
            self.client.get_sgv(count=1)

if __name__ == '__main__':
    unittest.main()
