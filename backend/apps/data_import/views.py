import os
import json

from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CorpusData
from .serializers import CorpusDataSerializer

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'json'}


def build_stats():
    """统计各文件类型数量"""
    counts = {t: 0 for t in ALLOWED_TYPES}
    qs = CorpusData.objects.values('fileType')
    for row in qs:
        ft = row['fileType']
        if ft in counts:
            counts[ft] += 1
    total = sum(counts.values())
    return {'counts': counts, 'total': total}


@csrf_exempt
@require_http_methods(["POST"])
def upload_data(request):
    """上传文件 -> 保存到磁盘 -> 解析/占位 -> 入库 -> 返回统计"""
    up_file = request.FILES.get('file')
    if not up_file:
        return JsonResponse({"error": "缺少文件"}, status=400)

    ext = up_file.name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        return JsonResponse({"error": f"不支持的文件类型: {ext}"}, status=400)

    # 保存原文件
    save_dir = 'uploads'
    file_path = os.path.join(save_dir, up_file.name)
    os.makedirs(save_dir, exist_ok=True)
    with default_storage.open(file_path, 'wb+') as dst:
        for chunk in up_file.chunks():
            dst.write(chunk)

    # 简单解析：txt/json读文本；其它存占位说明
    try:
        if ext == 'txt':
            up_file.seek(0)
            content = up_file.read().decode(errors='ignore')[:10000]
        elif ext == 'json':
            up_file.seek(0)
            raw = up_file.read().decode(errors='ignore')
            # 格式化/截断
            try:
                parsed = json.loads(raw)
                content = json.dumps(parsed, ensure_ascii=False)[:10000]
            except Exception:
                content = raw[:10000]
        else:
            content = f"已上传文件：{up_file.name}"
    except Exception as e:
        content = f"解析失败：{e}"

    obj = CorpusData.objects.create(
        fileType=ext,
        original_filename=up_file.name,
        content=content,
        status='已解析'
    )

    stats = build_stats()
    return JsonResponse({
        "message": "上传成功",
        "item": {
            "id": obj.id,
            "fileType": obj.fileType,
            "original_filename": obj.original_filename,
            "status": obj.status
        },
        "stats": stats
    })


@require_http_methods(["GET"])
def corpus_data(request):
    """查询语料（可搜索/按类型筛选）"""
    query = request.GET.get('query', '').strip()
    file_type = request.GET.get('file_type', '').strip().lower()

    data = CorpusData.objects.all().order_by('-id')
    if query:
        data = data.filter(content__icontains=query)
    if file_type:
        data = data.filter(fileType=file_type)

    serializer = CorpusDataSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
def stats(request):
    """文件类型统计"""
    return JsonResponse(build_stats())
