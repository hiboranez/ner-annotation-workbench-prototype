# python
from typing import Optional

from django.db.models import QuerySet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from .models import CorpusData
from .responses import ok
from .serializers import CorpusDataSerializer


def _query_after(last_id: int, file_type: Optional[str], limit: int) -> QuerySet:
    qs = CorpusData.objects.filter(id__gt=last_id).order_by("id")
    if file_type:
        qs = qs.filter(fileType=file_type.lower())
    return qs[:limit]


@api_view(["GET"])
@permission_classes([AllowAny])
def sync_after(request: Request):
    """增量同步：返回 id > last_id 的记录（升序），支持 file_type 过滤与 limit。"""
    try:
        last_id = int(request.query_params.get("last_id", "0"))
    except Exception:
        last_id = 0
    try:
        limit = max(1, min(500, int(request.query_params.get("limit", "100"))))
    except Exception:
        limit = 100
    file_type = (request.query_params.get("file_type") or "").strip().lower() or None

    qs = _query_after(last_id, file_type, limit)
    data = CorpusDataSerializer(qs, many=True).data
    new_last_id = data[-1]["id"] if data else last_id
    return ok({"results": data, "last_id": new_last_id})
