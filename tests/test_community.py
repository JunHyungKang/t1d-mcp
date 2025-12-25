import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from community.search import HybridSearchClient

class TestHybridSearch(unittest.TestCase):
    def setUp(self):
        # Mock env vars
        os.environ["NAVER_CLIENT_ID"] = "test_id"
        os.environ["NAVER_CLIENT_SECRET"] = "test_secret"
        os.environ["KAKAO_API_KEY"] = "test_key"
        self.client = HybridSearchClient()

    @patch('requests.get')
    def test_naver_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"title": "Test Blog", "link": "http://blog.naver.com"}]
        }
        mock_get.return_value = mock_response

        results = self.client.search_naver_blog("diabetes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], "Naver Blog")

    @patch('requests.get')
    def test_kakao_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "documents": [{"title": "Test Web", "url": "http://kakao.com"}]
        }
        mock_get.return_value = mock_response

        results = self.client.search_kakao_web("diabetes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], "Kakao Web")

if __name__ == '__main__':
    unittest.main()
