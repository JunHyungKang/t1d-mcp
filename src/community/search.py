import os
import requests
from typing import List, Dict, Any, Optional

class HybridSearchClient:
    def __init__(self):
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.kakao_api_key = os.getenv("KAKAO_API_KEY")

    def search_naver_blog(self, query: str, count: int = 3) -> List[Dict[str, str]]:
        if not self.naver_client_id or not self.naver_client_secret:
            return []
        
        url = "https://openapi.naver.com/v1/search/blog.json"
        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret
        }
        params = {"query": query, "display": count, "sort": "sim"}
        
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{"title": item["title"], "link": item["link"], "source": "Naver Blog"} for item in data.get("items", [])]
        except Exception as e:
            print(f"Naver Search Error: {e}")
            return []

    def search_kakao_web(self, query: str, count: int = 3) -> List[Dict[str, str]]:
        if not self.kakao_api_key:
            return []

        url = "https://dapi.kakao.com/v2/search/web"
        headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
        params = {"query": query, "size": count}

        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [{"title": item["title"], "link": item["url"], "source": "Kakao Web"} for item in data.get("documents", [])]
        except Exception as e:
            print(f"Kakao Search Error: {e}")
            return []

    def search_hybrid(self, query: str) -> List[Dict[str, str]]:
        """
        Combines results from Naver and Kakao.
        """
        naver_results = self.search_naver_blog(query)
        kakao_results = self.search_kakao_web(query)
        return naver_results + kakao_results
