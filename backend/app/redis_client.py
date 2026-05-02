"""
本地开发：用内存字典模拟 Redis（TTL 不精确，但功能够用）
生产/Docker：USE_REDIS=true 时连真实 Redis
"""
import time
from app.config import settings


class _MemoryCache:
    """轻量内存缓存，模拟 Redis get/setex 接口"""

    def __init__(self):
        self._store: dict[str, tuple[str, float]] = {}  # key → (value, expire_at)

    def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expire_at = entry
        if expire_at and time.time() > expire_at:
            del self._store[key]
            return None
        return value

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = (value, time.time() + ttl)

    def set(self, key: str, value: str) -> None:
        self._store[key] = (value, 0.0)


_memory_cache = _MemoryCache()
_redis_client = None


def get_redis():
    global _redis_client
    if settings.use_redis:
        if _redis_client is None:
            import redis
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        return _redis_client
    return _memory_cache
