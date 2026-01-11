"""
Redis Cache Layer for T1D Manager MCP Server

Redis 기반 캐싱 레이어. Redis가 없어도 서비스는 정상 동작 (graceful degradation).

Usage:
    from src.cache import cached

    @cached(key_prefix="t1d:search", ttl=30*24*60*60)
    def search_hybrid(query: str) -> List[Dict]:
        ...
"""

import os
import re
import json
import hashlib
from typing import Optional, Callable, Any, Tuple, Dict
from functools import wraps


# 한글 조사 패턴 (단어 끝에 붙는 조사들)
# 순서 중요: 긴 패턴을 먼저 매칭해야 함
# 주의: 일반 단어의 일부와 겹치지 않도록 주의 (예: "서" 제외 - "센서", "선서" 등)
KOREAN_PARTICLES = [
    # 복합 조사 (먼저 처리)
    r'에서는', r'에서도', r'으로는', r'으로도', r'에로', r'으로',
    r'에서', r'하기', r'처럼', r'보다', r'까지', r'부터', r'마저', r'조차',
    # 단일 조사 (흔한 단어 일부와 겹치는 것 제외)
    r'을', r'를', r'이', r'가', r'은', r'는', r'의', r'에', r'로', r'와', r'과',
    r'도', r'만',
]

# 정규식 패턴 컴파일 (성능 최적화)
PARTICLE_PATTERN = re.compile(
    r'(' + '|'.join(KOREAN_PARTICLES) + r')(?=\s|$)',
    re.UNICODE
)


def normalize_query(query: str) -> str:
    """
    검색 쿼리를 정규화하여 유사한 쿼리들이 같은 캐시 키를 생성하도록 함.

    정규화 단계:
    1. 소문자 변환 (영문)
    2. 특수문자 제거
    3. 한글 조사 제거
    4. 연속 공백 정규화
    5. 앞뒤 공백 제거

    Args:
        query: 원본 검색 쿼리

    Returns:
        정규화된 쿼리 문자열

    Examples:
        >>> normalize_query("저혈당을 간식")
        "저혈당 간식"
        >>> normalize_query("Type 1 Diabetes")
        "type 1 diabetes"
        >>> normalize_query("인슐린 계산하기")
        "인슐린 계산"
    """
    if not query:
        return ""

    # 1. 소문자 변환
    result = query.lower()

    # 2. 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
    result = re.sub(r'[^\w\s가-힣]', ' ', result)

    # 3. 한글 조사 제거
    result = PARTICLE_PATTERN.sub('', result)

    # 4. 연속 공백을 단일 공백으로
    result = re.sub(r'\s+', ' ', result)

    # 5. 앞뒤 공백 제거
    result = result.strip()

    return result


def _generate_cache_key(prefix: str, args: Tuple, kwargs: Dict, normalize: bool = False) -> str:
    """
    Generate a unique cache key from function arguments.

    Args:
        prefix: 캐시 키 접두사
        args: 함수 인자들
        kwargs: 함수 키워드 인자들
        normalize: True면 문자열 인자를 정규화하여 유사 쿼리가 같은 키 생성

    Returns:
        캐시 키 문자열 (예: "t1d:search:abc123...")
    """
    # self 인자 제외 (메서드의 경우 첫 번째 인자가 self)
    # args[0]이 객체 인스턴스인 경우 제외
    filtered_args = []
    for arg in args:
        if hasattr(arg, '__dict__') and not isinstance(arg, (str, int, float, list, dict)):
            continue  # Skip object instances

        # normalize=True이고 문자열이면 정규화
        if normalize and isinstance(arg, str):
            filtered_args.append(normalize_query(arg))
        else:
            filtered_args.append(arg)

    # kwargs도 정규화 (문자열 값만)
    normalized_kwargs = {}
    for k, v in kwargs.items():
        if normalize and isinstance(v, str):
            normalized_kwargs[k] = normalize_query(v)
        else:
            normalized_kwargs[k] = v

    arg_str = json.dumps([filtered_args, normalized_kwargs], sort_keys=True, ensure_ascii=False)
    # SHA-256 사용 (MD5보다 충돌 가능성 낮음)
    key_hash = hashlib.sha256(arg_str.encode()).hexdigest()[:32]
    return f"{prefix}:{key_hash}"


class CacheClient:
    """
    Optional Redis cache layer with graceful degradation.

    Redis가 사용 불가능할 경우에도 에러 없이 동작합니다.
    모든 작업은 조용히 실패하고 기본값을 반환합니다.
    """

    def __init__(self):
        self.client = self._init_redis()
        self.enabled = self.client is not None

    def _init_redis(self) -> Optional[Any]:
        """Redis 연결 초기화. 실패 시 None 반환."""
        try:
            import redis
            client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Health check
            client.ping()
            return client
        except ImportError:
            print("Redis library not installed. Caching disabled.")
            return None
        except Exception as e:
            print(f"Redis unavailable, caching disabled: {e}")
            return None

    def get(self, key: str) -> Optional[str]:
        """캐시에서 값을 가져옵니다. 실패 시 None 반환."""
        if not self.enabled:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: int) -> bool:
        """캐시에 값을 저장합니다. TTL은 초 단위. 실패 시 False 반환."""
        if not self.enabled:
            return False
        try:
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def delete(self, pattern: str) -> int:
        """
        패턴에 맞는 키들을 삭제합니다.

        SCAN 명령어 사용 (KEYS는 프로덕션에서 블로킹 위험)

        Args:
            pattern: Redis 키 패턴 (예: "t1d:search:*")

        Returns:
            삭제된 키 개수. 실패 시 0.
        """
        if not self.enabled:
            return 0
        try:
            # SCAN 사용 (비블로킹, 프로덕션 안전)
            cursor = 0
            deleted_count = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted_count += self.client.delete(*keys)
                if cursor == 0:
                    break
            return deleted_count
        except Exception as e:
            print(f"Redis delete error: {e}")
            return 0

    def clear_search_cache(self) -> int:
        """검색 캐시 전체 삭제."""
        return self.delete("t1d:search:*")


# Global cache instance
cache = CacheClient()


def cached(key_prefix: str, ttl: int = 30 * 24 * 60 * 60, normalize: bool = False):
    """
    함수 결과를 캐싱하는 데코레이터.

    Args:
        key_prefix: 캐시 키 접두사 (예: "t1d:search")
        ttl: Time-To-Live in seconds (기본: 30일)
        normalize: True면 문자열 인자를 정규화하여 유사 쿼리가 같은 캐시 사용
                   (한글 조사 제거, 소문자 변환, 특수문자 제거)

    Usage:
        @cached(key_prefix="t1d:search", ttl=2592000, normalize=True)
        def search_hybrid(self, query: str) -> List[Dict]:
            ...

    Notes:
        - 빈 결과 ([], {}, None)는 캐시하지 않습니다.
        - Redis 연결 실패 시에도 원본 함수는 정상 실행됩니다.
        - self 인자는 캐시 키 생성에서 제외됩니다.
        - normalize=True: "저혈당을 간식" ≈ "저혈당 간식" (같은 캐시 키)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key (with optional normalization)
            cache_key = _generate_cache_key(key_prefix, args, kwargs, normalize=normalize)

            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass  # Invalid cache, proceed to fetch

            # Cache miss - execute function
            result = func(*args, **kwargs)

            # Store in cache (skip empty results)
            if result:  # Non-empty result
                try:
                    serialized = json.dumps(result, ensure_ascii=False)
                    cache.set(cache_key, serialized, ttl)
                except (TypeError, ValueError) as e:
                    print(f"Cache serialization error: {e}")

            return result
        return wrapper
    return decorator
