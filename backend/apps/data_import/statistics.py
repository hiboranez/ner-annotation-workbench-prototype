# python

from .cache_utils import stats_cached
from .models import CorpusData

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'json'}


def _compute_stats():
    counts = {t: 0 for t in ALLOWED_TYPES}
    for row in CorpusData.objects.values('fileType'):
        ft = row['fileType']
        if ft in counts:
            counts[ft] += 1
    total = sum(counts.values())
    return {"counts": counts, "total": total}


def build_stats(force_compute: bool = False):
    """
    优先返回缓存；当 force_compute=True 时总是重新计算并写缓存。
    """
    if force_compute:
        data = _compute_stats()
        # 使用封装写入（绕过 get_or_set 的读）
        from django.conf import settings
        from .cache_utils import cache_set, KEY_STATS_GLOBAL
        ttl = getattr(settings, "APP_CACHE_TTLS", {}).get("STATS_GLOBAL_TTL", 60)
        cache_set(KEY_STATS_GLOBAL, data, ttl)
        return data

    return stats_cached(_compute_stats)
