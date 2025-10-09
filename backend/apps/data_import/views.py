# backend/apps/data_import/views.py
# python

import os
import uuid

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

from .cache_utils import (
    recent_corpus_cached,
    search_corpus_cached,
    invalidate_stats_cache,
    invalidate_recent_cache,
    invalidate_search_cache,
)
from .models import CorpusData
from .responses import fail
from .responses import ok
from .serializers import CorpusDataSerializer
from .statistics import ALLOWED_TYPES
from .statistics import build_stats

# 上传目录（与 exports 同级策略，避免依赖 MEDIA_ROOT）
UPLOAD_DIR = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "uploads", "corpus")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser])
def upload_view(request):
    """
    接收单文件上传，落盘后创建记录并异步解析。
    表单字段: file
    返回: { id, fileType, status }
    """
    f = request.FILES.get("file")
    if not f:
        return fail("缺少文件字段 `file`", code=4001, status=400)

    original = getattr(f, "name", "") or "unnamed"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED_TYPES:
        return fail(f"不支持的文件类型: {ext}", code=4002, status=400)

    # 先创建记录，标记解析中
    obj = CorpusData.objects.create(
        fileType=ext, original_filename=original, status="解析中", content=""
    )

    # 保存文件到本地，供 Celery 解析
    fname = f"{uuid.uuid4().hex}.{ext}"
    fpath = os.path.join(UPLOAD_DIR, fname)
    with open(fpath, "wb") as dst:
        for chunk in f.chunks():
            dst.write(chunk)

    # 触发解析任务
    from .tasks import parse_corpus_task
    parse_corpus_task.delay(obj.id, ext, fpath)

    return ok({"id": obj.id, "fileType": ext, "status": obj.status})


@api_view(["GET"])
@permission_classes([AllowAny])
def stats_view(_request):
    """
    返回聚合统计（plain JSON，前端按 d.counts 取值）
    """
    data = build_stats(force_compute=False)
    return JsonResponse({"counts": data["counts"], "total": data["total"]})


def _serialize_corpus(qs):
    return list(qs.values("id", "fileType", "content", "status").order_by("-id"))


@api_view(["GET"])
@permission_classes([AllowAny])
def corpus_list(request):
    """
    简化列表接口：支持 query / file_type 过滤。
    返回 plain JSON 数组，便于前端直接 merge。
    带 query 或 file_type 时走 search:{hash} 缓存；否则走 corpus:recent。
    """
    query = (request.query_params.get("query") or "").strip()
    file_type = (request.query_params.get("file_type") or "").strip().lower()
    has_filter = bool(query or file_type)

    def _fetch():
        qs = CorpusData.objects.all()
        if file_type:
            qs = qs.filter(fileType=file_type)
        if query:
            # 使用 trigram 相似度进行查询，利用 GIN 索引
            # 相似度阈值可根据需要调整
            qs = qs.annotate(
                similarity=TrigramSimilarity('content', query) + TrigramSimilarity('original_filename', query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

        # 限制返回规模，前端再分页
        qs = qs.order_by("-id")[:300]
        ser = CorpusDataSerializer(qs, many=True).data
        # 仅返回前端实际使用字段
        return [{"id": r["id"], "fileType": r["fileType"], "content": r["content"], "status": r["status"]} for r in ser]

    if has_filter:
        data = search_corpus_cached(query, file_type, _fetch)
    else:
        data = recent_corpus_cached(_fetch)

    return JsonResponse(data, safe=False)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def corpus_delete(_request, pk: int):
    try:
        obj = CorpusData.objects.get(pk=pk)
    except CorpusData.DoesNotExist:
        raise Http404
    obj.delete()
    # signals 会完成广播与缓存失效
    return ok({"id": pk})


@api_view(["POST"])
@permission_classes([AllowAny])
def cache_refresh_view(request):
    """
    手动刷新缓存。POST JSON: { "targets": ["stats","recent","search","all"] }
    返回各项删除数量，若包含 stats 则顺带重算一次。
    """
    try:
        targets = request.data.get("targets") or []
        if not isinstance(targets, list):
            targets = []
    except Exception:
        targets = []

    deleted = {}
    if "all" in targets:
        # 统一删除
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

    # 如果删了 stats，重算写入
    if "all" in targets or "stats" in targets:
        build_stats(force_compute=True)

    return ok({"deleted": deleted})
