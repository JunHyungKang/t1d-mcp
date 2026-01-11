"""
Tests for the caching layer.

TDD 방식으로 작성:
1. Redis 없을 때 graceful degradation 테스트
2. @cached 데코레이터 동작 테스트
3. Cache hit/miss 시나리오 테스트
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestCacheClient(unittest.TestCase):
    """CacheClient 기본 동작 테스트"""

    def test_cache_disabled_when_redis_unavailable(self):
        """Redis 연결 실패 시에도 에러 없이 동작해야 함"""
        from cache import CacheClient

        # Redis 연결 실패 시뮬레이션 (기본 환경에서는 Redis 없음)
        cache = CacheClient()

        # get은 None 반환
        result = cache.get("nonexistent_key")
        self.assertIsNone(result)

        # set은 False 반환 (저장 실패)
        success = cache.set("test_key", "test_value", 3600)
        self.assertFalse(success)

        # delete은 0 반환 (삭제된 키 없음)
        deleted = cache.delete("test:*")
        self.assertEqual(deleted, 0)

    @patch('redis.Redis')
    def test_cache_enabled_when_redis_available(self, mock_redis_cls):
        """Redis 연결 성공 시 캐시 활성화"""
        from cache import CacheClient

        # Mock Redis 설정
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis_cls.return_value = mock_redis

        cache = CacheClient()

        self.assertTrue(cache.enabled)
        self.assertIsNotNone(cache.client)

    @patch('redis.Redis')
    def test_get_returns_cached_value(self, mock_redis_cls):
        """캐시된 값을 정상적으로 반환해야 함"""
        from cache import CacheClient

        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = '{"test": "data"}'
        mock_redis_cls.return_value = mock_redis

        cache = CacheClient()
        result = cache.get("test_key")

        self.assertEqual(result, '{"test": "data"}')
        mock_redis.get.assert_called_once_with("test_key")

    @patch('redis.Redis')
    def test_set_stores_value_with_ttl(self, mock_redis_cls):
        """TTL과 함께 값을 저장해야 함"""
        from cache import CacheClient

        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis_cls.return_value = mock_redis

        cache = CacheClient()
        ttl = 30 * 24 * 60 * 60  # 30 days
        success = cache.set("test_key", '{"test": "data"}', ttl)

        self.assertTrue(success)
        mock_redis.setex.assert_called_once_with("test_key", ttl, '{"test": "data"}')

    @patch('redis.Redis')
    def test_delete_removes_matching_keys(self, mock_redis_cls):
        """패턴에 맞는 키들을 삭제해야 함 (SCAN 사용)"""
        from cache import CacheClient

        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        # SCAN returns (cursor, keys) - 0 means scan complete
        mock_redis.scan.return_value = (0, ["t1d:search:query1", "t1d:search:query2"])
        mock_redis.delete.return_value = 2
        mock_redis_cls.return_value = mock_redis

        cache = CacheClient()
        deleted = cache.delete("t1d:search:*")

        self.assertEqual(deleted, 2)
        mock_redis.scan.assert_called_once_with(0, match="t1d:search:*", count=100)

    @patch('redis.Redis')
    def test_graceful_degradation_on_redis_error(self, mock_redis_cls):
        """Redis 에러 시에도 예외 없이 기본값 반환"""
        from cache import CacheClient

        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.side_effect = Exception("Redis connection lost")
        mock_redis_cls.return_value = mock_redis

        cache = CacheClient()
        result = cache.get("test_key")

        # 예외가 발생해도 None 반환
        self.assertIsNone(result)


class TestCachedDecorator(unittest.TestCase):
    """@cached 데코레이터 테스트"""

    def test_decorator_calls_function_on_cache_miss(self):
        """캐시 미스 시 원본 함수 호출"""
        from cache import cached

        call_count = 0

        @cached(key_prefix="test", ttl=3600)
        def expensive_function(x: int) -> dict:
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        result = expensive_function(5)

        self.assertEqual(result, {"result": 10})
        self.assertEqual(call_count, 1)

    @patch('cache.cache')
    def test_decorator_returns_cached_value_on_hit(self, mock_cache):
        """캐시 히트 시 캐시된 값 반환"""
        from cache import cached

        # 캐시 히트 시뮬레이션
        mock_cache.get.return_value = json.dumps({"result": 10})

        call_count = 0

        @cached(key_prefix="test", ttl=3600)
        def expensive_function(x: int) -> dict:
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        result = expensive_function(5)

        self.assertEqual(result, {"result": 10})
        # 캐시 히트이므로 함수는 호출되지 않음
        self.assertEqual(call_count, 0)

    @patch('cache.cache')
    def test_decorator_stores_result_on_miss(self, mock_cache):
        """캐시 미스 시 결과를 캐시에 저장"""
        from cache import cached

        mock_cache.get.return_value = None  # Cache miss

        @cached(key_prefix="test", ttl=3600)
        def expensive_function(x: int) -> dict:
            return {"result": x * 2}

        result = expensive_function(5)

        # 결과가 캐시에 저장되었는지 확인
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        self.assertEqual(call_args[0][2], 3600)  # TTL 확인
        stored_value = json.loads(call_args[0][1])
        self.assertEqual(stored_value, {"result": 10})

    @patch('cache.cache')
    def test_decorator_skips_caching_empty_results(self, mock_cache):
        """빈 결과는 캐시하지 않음"""
        from cache import cached

        mock_cache.get.return_value = None

        @cached(key_prefix="test", ttl=3600)
        def return_empty() -> list:
            return []

        result = return_empty()

        self.assertEqual(result, [])
        # 빈 결과는 캐시에 저장하지 않음
        mock_cache.set.assert_not_called()

    def test_decorator_generates_unique_keys_for_different_args(self):
        """다른 인자에 대해 다른 캐시 키 생성"""
        from cache import cached, _generate_cache_key

        key1 = _generate_cache_key("test", (1,), {})
        key2 = _generate_cache_key("test", (2,), {})
        key3 = _generate_cache_key("test", (1,), {"extra": "arg"})

        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key1, key3)
        self.assertTrue(key1.startswith("test:"))


class TestQueryNormalization(unittest.TestCase):
    """쿼리 정규화 테스트"""

    def test_normalize_removes_korean_particles(self):
        """한글 조사를 제거해야 함"""
        from cache import normalize_query

        # 목적격 조사
        self.assertEqual(normalize_query("저혈당을 간식"), "저혈당 간식")
        self.assertEqual(normalize_query("인슐린을 계산"), "인슐린 계산")

        # 주격 조사
        self.assertEqual(normalize_query("혈당이 높다"), "혈당 높다")
        self.assertEqual(normalize_query("인슐린이 필요"), "인슐린 필요")

        # 관형격 조사
        self.assertEqual(normalize_query("인슐린의 용량"), "인슐린 용량")

        # 보조사
        self.assertEqual(normalize_query("저혈당은 위험"), "저혈당 위험")
        self.assertEqual(normalize_query("혈당는 정상"), "혈당 정상")

    def test_normalize_handles_location_particles(self):
        """위치/방향 조사 처리"""
        from cache import normalize_query

        self.assertEqual(normalize_query("병원에 가다"), "병원 가다")
        self.assertEqual(normalize_query("병원에서 검사"), "병원 검사")
        self.assertEqual(normalize_query("집으로 가다"), "집 가다")
        self.assertEqual(normalize_query("집에로 가다"), "집 가다")

    def test_normalize_removes_action_particles(self):
        """동작 관련 조사 제거"""
        from cache import normalize_query

        self.assertEqual(normalize_query("인슐린 계산하기"), "인슐린 계산")
        self.assertEqual(normalize_query("혈당 측정하기"), "혈당 측정")

    def test_normalize_lowercase_english(self):
        """영문은 소문자로 변환"""
        from cache import normalize_query

        self.assertEqual(normalize_query("Type 1 Diabetes"), "type 1 diabetes")
        self.assertEqual(normalize_query("CGM 센서"), "cgm 센서")

    def test_normalize_removes_special_characters(self):
        """특수문자 제거"""
        from cache import normalize_query

        self.assertEqual(normalize_query("저혈당? 간식!"), "저혈당 간식")
        self.assertEqual(normalize_query("인슐린...계산"), "인슐린 계산")

    def test_normalize_handles_multiple_spaces(self):
        """연속 공백을 단일 공백으로"""
        from cache import normalize_query

        self.assertEqual(normalize_query("저혈당   간식"), "저혈당 간식")
        self.assertEqual(normalize_query("  인슐린  계산  "), "인슐린 계산")

    def test_normalize_preserves_word_boundaries(self):
        """단어 경계(공백)는 유지"""
        from cache import normalize_query

        # 띄어쓰기는 유지되어야 함
        result = normalize_query("저혈당 간식 추천")
        self.assertIn(" ", result)

    def test_similar_queries_produce_same_normalized_form(self):
        """유사한 쿼리들이 같은 정규화 결과 생성"""
        from cache import normalize_query

        # 조사만 다른 경우 같은 결과
        q1 = normalize_query("저혈당을 간식")
        q2 = normalize_query("저혈당 간식")
        q3 = normalize_query("저혈당의 간식")
        self.assertEqual(q1, q2)
        self.assertEqual(q2, q3)

        # 하기 접미사
        q4 = normalize_query("인슐린 계산하기")
        q5 = normalize_query("인슐린 계산")
        self.assertEqual(q4, q5)


class TestCachedDecoratorWithNormalization(unittest.TestCase):
    """정규화 옵션을 사용하는 @cached 데코레이터 테스트"""

    @patch('cache.cache')
    def test_normalize_option_matches_similar_queries(self, mock_cache):
        """normalize=True일 때 유사 쿼리가 같은 캐시 사용"""
        from cache import cached

        # 첫 번째 쿼리로 캐시 저장
        mock_cache.get.return_value = None
        stored_keys = []

        def capture_key(key, value, ttl):
            stored_keys.append(key)
            return True
        mock_cache.set.side_effect = capture_key

        @cached(key_prefix="test", ttl=3600, normalize=True)
        def search(query: str) -> dict:
            return {"query": query}

        # 첫 번째 호출 - 캐시 저장
        search("저혈당을 간식")

        # 두 번째 호출 - 같은 캐시 키 사용해야 함
        mock_cache.get.return_value = json.dumps({"query": "저혈당을 간식"})

        # 조사만 다른 쿼리로 호출
        result = search("저혈당 간식")

        # 같은 캐시 키로 조회했는지 확인
        get_calls = mock_cache.get.call_args_list
        self.assertEqual(len(get_calls), 2)
        # 두 호출의 캐시 키가 동일해야 함
        self.assertEqual(get_calls[0][0][0], get_calls[1][0][0])

    def test_normalize_false_keeps_original_behavior(self):
        """normalize=False(기본값)일 때 기존 동작 유지"""
        from cache import _generate_cache_key

        # normalize 없이 (기본값) 다른 키 생성
        key1 = _generate_cache_key("test", ("저혈당을 간식",), {}, normalize=False)
        key2 = _generate_cache_key("test", ("저혈당 간식",), {}, normalize=False)

        self.assertNotEqual(key1, key2)


class TestCacheIntegrationWithSearch(unittest.TestCase):
    """검색 기능과 캐시 통합 테스트"""

    @patch('src.cache.cache')
    @patch('requests.get')
    def test_search_uses_cache(self, mock_get, mock_cache):
        """검색 결과가 캐시에서 제공되어야 함"""
        # 환경변수 설정
        os.environ["NAVER_CLIENT_ID"] = "test_id"
        os.environ["NAVER_CLIENT_SECRET"] = "test_secret"
        os.environ["KAKAO_API_KEY"] = "test_key"

        # Need to reimport to get the patched version
        import importlib
        import src.community.search as search_module
        importlib.reload(search_module)
        from src.community.search import HybridSearchClient

        cached_result = [
            {"title": "Cached Blog", "link": "http://cached.com", "source": "Naver Blog"}
        ]
        mock_cache.get.return_value = json.dumps(cached_result)

        client = HybridSearchClient()
        result = client.search_hybrid("저혈당 간식")

        # 캐시에서 결과를 가져왔으므로 API 호출 없음
        mock_get.assert_not_called()
        self.assertEqual(result, cached_result)

    @patch('src.cache.cache')
    @patch('requests.get')
    def test_search_fetches_and_caches_on_miss(self, mock_get, mock_cache):
        """캐시 미스 시 API 호출 후 캐시 저장"""
        os.environ["NAVER_CLIENT_ID"] = "test_id"
        os.environ["NAVER_CLIENT_SECRET"] = "test_secret"
        os.environ["KAKAO_API_KEY"] = "test_key"

        import importlib
        import src.community.search as search_module
        importlib.reload(search_module)
        from src.community.search import HybridSearchClient

        mock_cache.get.return_value = None  # Cache miss

        # Mock API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"items": [{"title": "Naver Blog", "link": "http://naver.com"}]},
            {"documents": [{"title": "Kakao Web", "url": "http://kakao.com"}]}
        ]
        mock_get.return_value = mock_response

        client = HybridSearchClient()
        result = client.search_hybrid("저혈당 간식")

        # API가 호출됨
        self.assertEqual(mock_get.call_count, 2)

        # 결과가 캐시에 저장됨
        mock_cache.set.assert_called_once()


if __name__ == '__main__':
    unittest.main()
