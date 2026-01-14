import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cgm.nightscout import NightscoutClient
from cgm.dexcom import DexcomClient
from cgm.dexcom_official import DexcomOfficialClient, format_egvs_for_display

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


class TestDexcomOfficialClient(unittest.TestCase):
    """Dexcom Developer API (Official) 클라이언트 테스트"""
    
    def setUp(self):
        self.client = DexcomOfficialClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback",
            sandbox=True
        )
    
    def test_initialization(self):
        """클라이언트 초기화 테스트"""
        self.assertEqual(self.client.client_id, "test_client_id")
        self.assertEqual(self.client.base_url, "https://sandbox-api.dexcom.com")
        self.assertTrue(self.client.sandbox)
    
    def test_get_authorization_url(self):
        """Authorization URL 생성 테스트"""
        url = self.client.get_authorization_url(state="test_state")
        
        self.assertIn("https://sandbox-api.dexcom.com/v2/oauth2/login", url)
        self.assertIn("client_id=test_client_id", url)
        self.assertIn("redirect_uri=http://localhost:8080/callback", url)
        self.assertIn("response_type=code", url)
        self.assertIn("scope=offline_access", url)
        self.assertIn("state=test_state", url)
    
    def test_production_base_url(self):
        """Production 환경 URL 테스트"""
        prod_client = DexcomOfficialClient(
            client_id="test",
            client_secret="test",
            sandbox=False
        )
        self.assertEqual(prod_client.base_url, "https://api.dexcom.com")


class TestFormatEgvsForDisplay(unittest.TestCase):
    """EGV 데이터 포맷팅 테스트"""
    
    def test_format_empty_data(self):
        """빈 데이터 포맷팅"""
        result = format_egvs_for_display({"records": []})
        self.assertIn("데이터가 없습니다", result)
    
    def test_format_with_records(self):
        """실제 데이터 포맷팅"""
        egvs_data = {
            "records": [
                {
                    "value": 120,
                    "trend": "flat",
                    "systemTime": "2025-12-25T12:00:00Z"
                },
                {
                    "value": 130,
                    "trend": "singleUp",
                    "systemTime": "2025-12-25T12:05:00Z"
                }
            ]
        }
        
        result = format_egvs_for_display(egvs_data, limit=5)
        
        self.assertIn("120", result)
        self.assertIn("130", result)
        self.assertIn("안정", result)  # flat → 안정
        self.assertIn("상승", result)  # singleUp → 상승
    
    def test_format_respects_limit(self):
        """limit 파라미터 동작 테스트"""
        egvs_data = {
            "records": [
                {"value": i, "trend": "flat", "systemTime": f"2025-12-25T12:{i:02d}:00Z"}
                for i in range(10)
            ]
        }
        
        result = format_egvs_for_display(egvs_data, limit=3)
        
        # "총 10개의 기록 중 3개만 표시" 메시지 확인
        self.assertIn("10개", result)
        self.assertIn("3개", result)


if __name__ == '__main__':
    unittest.main()
