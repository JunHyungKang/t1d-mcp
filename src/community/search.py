import os
import requests
from typing import List, Dict, Any, Optional

from src.cache import cached

# 30일 TTL (초 단위)
SEARCH_CACHE_TTL = 30 * 24 * 60 * 60


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
            # MCP Timeout is 10s, so we set a safe limit of 3s per API
            resp = requests.get(url, headers=headers, params=params, timeout=3.0)
            resp.raise_for_status()
            data = resp.json()
            return [{"title": item["title"], "link": item["link"], "source": "Naver Blog"} for item in data.get("items", [])]
        except requests.exceptions.Timeout:
            print("Naver Search Timeout (Skipping)")
            return []
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
            # Safe limit of 3s
            resp = requests.get(url, headers=headers, params=params, timeout=3.0)
            resp.raise_for_status()
            data = resp.json()
            return [{"title": item["title"], "link": item["url"], "source": "Kakao Web"} for item in data.get("documents", [])]
        except requests.exceptions.Timeout:
            print("Kakao Search Timeout (Skipping)")
            return []
        except Exception as e:
            print(f"Kakao Search Error: {e}")
            return []

    @cached(key_prefix="t1d:search", ttl=SEARCH_CACHE_TTL, normalize=True)
    def search_hybrid(self, query: str) -> List[Dict[str, str]]:
        """
        Combines results from Naver and Kakao.
        Automatically adds context for Type 1 Diabetes if missing.

        Results are cached in Redis for 30 days. Similar queries
        (e.g., "저혈당을 간식" ≈ "저혈당 간식") use the same cache entry.
        """
        # Enhance query for Type 1 Diabetes context if not present
        if "1형" not in query and "type 1" not in query.lower():
            enhanced_query = f"1형 당뇨 {query}"
        else:
            enhanced_query = query
            
        naver_results = self.search_naver_blog(enhanced_query)
        kakao_results = self.search_kakao_web(enhanced_query)
        return naver_results + kakao_results
