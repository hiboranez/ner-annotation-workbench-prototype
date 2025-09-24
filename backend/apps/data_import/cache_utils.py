# python
import hashlib
from typing import Any, Callable, Dict, Iterable, Optional

from django.conf import settings
from django.core.cache import cache

# 统一 Key 规范
KEY_STATS_GLOBAL = "stats:global"
KEY_CORPUS_RECENT = "corpus:recent"
KEY_SEARCH_PREFIX = "search:"  # 完整形式：search:{sha1}


def _ttls() -> Dict[str, int]:
    return getattr(settings, "APP_CACHE_TTLS", {
        "STATS_GLOBAL_TTL": 60,
        "RECENT_CORPUS_TTL": 60,
        "SEARCH_TTL": 300,
    })


def cache_get(key: str) -> Any:
    return cache.get(key)


def cache_set(key: str, value: Any, ttl: Optional[int]) -> None:
    # ttl=None 表示使用全局 TIMEOUT；我们按业务 TTL 控制
    cache.set(key, value, timeout=ttl)


def _make_search_hash(query: Optional[str], file_type: Optional[str]) -> str:
    q = (query or "").strip()
    ft = (file_type or "").strip().lower()
    # 稳定串联后 sha1
    raw = f"q={q}&ft={ft}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def make_search_key(query: Optional[str], file_type: Optional[str]) -> str:
    return f"{KEY_SEARCH_PREFIX}{_make_search_hash(query, file_type)}"


def get_or_set(key: str, producer: Callable[[], Any], ttl: Optional[int]) -> Any:
    val = cache_get(key)
    if val is not None:
        return val
    val = producer()
    cache_set(key, val, ttl)
    return val


def _redis_client():
    try:
        return cache.client.get_client(write=True)
    except Exception:
        return None


def delete_keys(keys: Iterable[str]) -> int:
    client = _redis_client()
    deleted = 0
    if client:
        # 将业务 key 转换成真实存储 key（包含前缀/版本）
        real_keys = [cache.make_key(k) for k in keys]
        if real_keys:
            deleted = client.delete(*real_keys)
    else:
        for k in keys:
            if cache.delete(k):
                deleted += 1
    return int(deleted)


def delete_pattern(pattern: str) -> int:
    """
    基于 Redis SCAN 的模式删除，适合 search:* 等。
    """
    client = _redis_client()
    if not client:
        # 回退：无法精准删除，只能尽量清空命中的几类键（不建议）
        return 0
    real_pat = cache.make_key(pattern)
    count = 0
    for k in client.scan_iter(match=real_pat, count=1000):
        try:
            client.delete(k)
            count += 1
        except Exception:
            pass
    return count


def invalidate_stats_cache() -> int:
    return delete_keys([KEY_STATS_GLOBAL])


def invalidate_recent_cache() -> int:
    return delete_keys([KEY_CORPUS_RECENT])


def invalidate_search_cache() -> int:
    return delete_pattern(f"{KEY_SEARCH_PREFIX}*")


def invalidate_all_corpus_caches() -> Dict[str, int]:
    return {
        "stats": invalidate_stats_cache(),
        "recent": invalidate_recent_cache(),
        "search": invalidate_search_cache(),
    }


def stats_cached(fetcher: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    ttl = _ttls().get("STATS_GLOBAL_TTL", 60)
    return get_or_set(KEY_STATS_GLOBAL, fetcher, ttl)


def recent_corpus_cached(fetcher: Callable[[], Any]) -> Any:
    ttl = _ttls().get("RECENT_CORPUS_TTL", 60)
    return get_or_set(KEY_CORPUS_RECENT, fetcher, ttl)


def search_corpus_cached(query: Optional[str], file_type: Optional[str], fetcher: Callable[[], Any]) -> Any:
    ttl = _ttls().get("SEARCH_TTL", 300)
    key = make_search_key(query, file_type)
    return get_or_set(key, fetcher, ttl)
