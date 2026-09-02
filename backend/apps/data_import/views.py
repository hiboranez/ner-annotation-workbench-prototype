import os
import time
import uuid

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser

from .cache_utils import (
    recent_corpus_cached,
    search_corpus_cached,
    invalidate_stats_cache,
    invalidate_recent_cache,
    invalidate_search_cache,
)
from .models import CorpusData
from .permissions import IsAdmin, IsAnnotatorOrAdmin, IsViewerOrAboveReadOnly
from .responses import fail, ok
from .serializers import CorpusDataSerializer
from .statistics import ALLOWED_TYPES
from .statistics import build_stats

# Prometheus 自定义指标：上传耗时
try:
    from prometheus_client import Histogram

    METRIC_UPLOAD_SECONDS = Histogram(
        'app_upload_seconds',
        'Upload duration in seconds',
        ['file_type', 'status']
    )
except Exception:  # noqa
    METRIC_UPLOAD_SECONDS = None

# 上传目录
UPLOAD_DIR = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "uploads", "corpus")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@api_view(["POST"])
@permission_classes([IsAnnotatorOrAdmin])
@parser_classes([MultiPartParser])
def upload_view(request):
    """
    接收单文件上传，落盘后创建记录并异步解析。
    仅 annotator/admin 允许。
    KPI: 记录上传耗时（写盘+调度前的总时长）。
    """
    started = time.perf_counter()
    ext = ""
    status_label = "error"
    try:
        f = request.FILES.get("file")
        if not f:
            return fail("缺少文件字段 `file`", code=4001, status=400)

        original = getattr(f, "name", "") or "unnamed"
        ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
        if ext not in ALLOWED_TYPES:
            return fail(f"不支持的文件类型: {ext}", code=4002, status=400)

        obj = CorpusData.objects.create(
            fileType=ext, original_filename=original, status="解析中", content=""
        )

        fname = f"{uuid.uuid4().hex}.{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as dst:
            for chunk in f.chunks():
                dst.write(chunk)

        from .tasks import parse_corpus_task
        parse_corpus_task.delay(obj.id, ext, fpath)

        status_label = "ok"
        return ok({"id": obj.id, "fileType": ext, "status": obj.status})
    finally:
        try:
            if METRIC_UPLOAD_SECONDS:
                duration = max(0.0, time.perf_counter() - started)
                METRIC_UPLOAD_SECONDS.labels(file_type=ext or "unknown", status=status_label).observe(duration)
        except Exception:
            pass


@api_view(["GET"])
@permission_classes([IsViewerOrAboveReadOnly])
def stats_view(_request):
    """
    返回聚合统计（仅登录用户，只读）
    """
    data = build_stats(force_compute=False)
    return JsonResponse({"counts": data["counts"], "total": data["total"]})


def _serialize_corpus(qs):
    return list(qs.values("id", "fileType", "content", "status").order_by("-id"))


@api_view(["GET"])
@permission_classes([IsViewerOrAboveReadOnly])
def corpus_list(request):
    """
    简化列表接口：支持 query / file_type 过滤。
    登录用户只读；带 query 或 file_type 时走 search 缓存，否则 recent。
    """
    query = (request.query_params.get("query") or "").strip()
    file_type = (request.query_params.get("file_type") or "").strip().lower()
    has_filter = bool(query or file_type)

    def _fetch():
        qs = CorpusData.objects.all()
        if file_type:
            qs = qs.filter(fileType=file_type)
        if query:
            qs = qs.annotate(
                similarity=TrigramSimilarity('content', query) + TrigramSimilarity('original_filename', query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

        qs = qs.order_by("-id")[:300]
        ser = CorpusDataSerializer(qs, many=True).data
        return [{"id": r["id"], "fileType": r["fileType"], "content": r["content"], "status": r["status"]} for r in ser]

    if has_filter:
        data = search_corpus_cached(query, file_type, _fetch)
    else:
        data = recent_corpus_cached(_fetch)

    return JsonResponse(data, safe=False)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def corpus_delete(_request, pk: int):
    try:
        obj = CorpusData.objects.get(pk=pk)
    except CorpusData.DoesNotExist:
        raise Http404
    obj.delete()
    return ok({"id": pk})


@api_view(["POST"])
@permission_classes([IsAdmin])
def cache_refresh_view(request):
    """
    手动刷新缓存（仅 admin）
    POST JSON: { "targets": ["stats","recent","search","all"] }
    """
    try:
        targets = request.data.get("targets") or []
        if not isinstance(targets, list):
            targets = []
    except Exception:
        targets = []

    deleted = {}
    if "all" in targets:
        deleted["stats"] = invalidate_stats_cache()
        deleted["recent"] = invalidate_recent_cache()
        deleted["search"] = invalidate_search_cache()
    else:
        if "stats" in targets:
            deleted["stats"] = invalidate_stats_cache()
        if "recent" in targets:
            deleted["recent"] = invalidate_recent_cache()
        if "search" in targets:
            deleted["search"] = invalidate_search_cache()

    if "all" in targets or "stats" in targets:
        build_stats(force_compute=True)

    return ok({"deleted": deleted})
