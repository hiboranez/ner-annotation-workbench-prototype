# python
import json
import logging
import os
import uuid
from typing import Iterable, List, Dict

from celery import shared_task, chord
from django.conf import settings
from django.db.models import Q

from .cache_utils import (
    KEY_STATS_GLOBAL,
    cache_set,
)
from .models import CorpusData
from .services import parse_content
from .statistics import build_stats

logger = logging.getLogger(__name__)

# Prometheus 指标（任务级）
try:
    from prometheus_client import Counter

    METRIC_TASK_SUCCESS = Counter('app_task_success_total', 'Task success total', ['task'])
    METRIC_TASK_FAILURE = Counter('app_task_failure_total', 'Task failure total', ['task'])
    METRIC_TASK_RETRY = Counter('app_task_retry_total', 'Task retry total', ['task'])
    # KPI: 解析尝试/失败计数
    METRIC_PARSE_TOTAL = Counter('app_parse_total', 'Total parse attempts', ['ext'])
    METRIC_PARSE_FAILED = Counter('app_parse_failed_total', 'Total parse failures', ['ext'])
except Exception:  # noqa
    METRIC_TASK_SUCCESS = METRIC_TASK_FAILURE = METRIC_TASK_RETRY = None
    METRIC_PARSE_TOTAL = METRIC_PARSE_FAILED = None


def _metric_inc(counter, *labels):
    try:
        if counter:
            if labels:
                counter.labels(*labels).inc()
            else:
                counter.inc()
    except Exception:
        pass


def _notify_warning(msg: str, extra: Dict = None):
    logger.warning(msg, extra=extra or {})


# ========== 解析任务（parsing） ==========
@shared_task(bind=True, max_retries=2)
def parse_corpus_task(self, corpus_id: int, ext: str, file_path: str):
    """
    解析上传文件，写入内容与状态。
    队列：parsing
    KPI: 解析失败率（app_parse_failed_total / app_parse_total）
    """
    task_name = 'parse_corpus_task'
    try:
        _metric_inc(METRIC_PARSE_TOTAL, ext or "unknown")
        try:
            obj = CorpusData.objects.get(id=corpus_id)
        except CorpusData.DoesNotExist:
            _notify_warning(f'[parse] corpus {corpus_id} not found')
            return

        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        content = parse_content(ext, file_bytes)
        obj.content = content
        obj.status = "已解析" if not content.startswith("解析失败") else "解析失败"
        obj.save(update_fields=["content", "status"])

        if obj.status != "已解析":
            _metric_inc(METRIC_PARSE_FAILED, ext or "unknown")

        _metric_inc(METRIC_TASK_SUCCESS, task_name)
    except Exception as e:
        _metric_inc(METRIC_TASK_FAILURE, task_name)
        _metric_inc(METRIC_PARSE_FAILED, ext or "unknown")
        _notify_warning(f'[parse] failed corpus_id={corpus_id}, err={e}')
        try:
            _metric_inc(METRIC_TASK_RETRY, task_name)
            raise self.retry(exc=e, countdown=min(60, 10 * (self.request.retries + 1)))
        except self.MaxRetriesExceededError:
            _notify_warning(f'[parse] max retries exceeded corpus_id={corpus_id}')


# ========== 统计预聚合（stats） ==========
@shared_task(bind=True)
def stats_preaggregate_task(self):
    """
    周期性预聚合统计并写入缓存。
    队列：stats
    """
    task_name = 'stats_preaggregate_task'
    try:
        data = build_stats(force_compute=True)  # 强制计算一次
        # 再次显式写入，确保 TTL 按配置
        ttl = getattr(settings, "APP_CACHE_TTLS", {}).get("STATS_GLOBAL_TTL", 60)
        cache_set(KEY_STATS_GLOBAL, data, ttl)
        _metric_inc(METRIC_TASK_SUCCESS, task_name)
        return data
    except Exception as e:
        _metric_inc(METRIC_TASK_FAILURE, task_name)
        _notify_warning(f'[stats] preaggregate failed: {e}')
        raise


# ========== 批量导出（export） ==========
EXPORT_DIR = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


def _query_ids(filters: Dict) -> List[int]:
    qs = CorpusData.objects.all().order_by('id')
    if filters.get('file_type'):
        qs = qs.filter(fileType=filters['file_type'])
    if filters.get('status'):
        qs = qs.filter(status=filters['status'])
    if filters.get('query'):
        q = filters['query']
        qs = qs.filter(Q(content__icontains=q) | Q(original_filename__icontains=q))
    return list(qs.values_list('id', flat=True))


def _chunks(iterable: Iterable[int], size: int) -> Iterable[List[int]]:
    chunk = []
    for x in iterable:
        chunk.append(x)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


@shared_task(bind=True)
def export_corpus_batch_task(self, id_list: List[int], export_id: str) -> str:
    """
    导出分片任务：把一批 id 序列化到临时 json 文件，返回文件路径。
    队列：export
    """
    task_name = 'export_corpus_batch_task'
    try:
        rows = list(
            CorpusData.objects.filter(id__in=id_list).values(
                'id', 'fileType', 'original_filename', 'content', 'status', 'created_at'
            ).order_by('id')
        )
        part_path = os.path.join(EXPORT_DIR, f'{export_id}.part.{uuid.uuid4().hex}.json')
        with open(part_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False)
        _metric_inc(METRIC_TASK_SUCCESS, task_name)
        return part_path
    except Exception as e:
        _metric_inc(METRIC_TASK_FAILURE, task_name)
        _notify_warning(f'[export-batch] export_id={export_id} failed: {e}')
        raise


@shared_task(bind=True)
def export_corpus_finalize_task(self, part_files: List[str], export_id: str) -> str:
    """
    汇总分片文件，合并为一个 JSON 文件并清理分片。
    队列：export
    """
    task_name = 'export_corpus_finalize_task'
    try:
        all_rows: List[Dict] = []
        for p in part_files:
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    all_rows.extend(json.load(f))
            finally:
                try:
                    os.remove(p)
                except Exception:
                    pass
        out_path = os.path.join(EXPORT_DIR, f'corpus_export_{export_id}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_rows, f, ensure_ascii=False, indent=2)
        _metric_inc(METRIC_TASK_SUCCESS, task_name)
        return out_path
    except Exception as e:
        _metric_inc(METRIC_TASK_FAILURE, task_name)
        _notify_warning(f'[export-finalize] export_id={export_id} failed: {e}')
        raise


@shared_task(bind=True)
def export_corpus_start_task(self, filters: Dict = None, batch_size: int = 200, export_id: str = None) -> str:
    """
    导出协调任务：根据过滤条件分片调度，再汇总输出。
    返回最终导出文件路径。
    队列：export
    """
    task_name = 'export_corpus_start_task'
    try:
        filters = filters or {}
        export_id = export_id or uuid.uuid4().hex
        ids = _query_ids(filters)
        if not ids:
            # 空导出也生成空文件
            return export_corpus_finalize_task.apply(args=[[], export_id]).get()

        parts = [export_corpus_batch_task.s(chunk, export_id) for chunk in _chunks(ids, batch_size)]
        result = chord(parts)(export_corpus_finalize_task.s(export_id))
        out_path = result.get()
        _metric_inc(METRIC_TASK_SUCCESS, task_name)
        return out_path
    except Exception as e:
        _metric_inc(METRIC_TASK_FAILURE, task_name)
        _notify_warning(f'[export-start] failed: {e}')
        raise
