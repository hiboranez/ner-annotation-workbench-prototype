import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CorpusData
from .serializers import CorpusDataSerializer
from .services import parse_content
from .statistics import build_stats
from .tasks import parse_corpus_task

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'json'}


@csrf_exempt
@require_http_methods(["POST"])
def upload_data(request):
    up_file = request.FILES.get('file')
    if not up_file:
        return JsonResponse({"error": "缺少文件"}, status=400)

    ext = up_file.name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        return JsonResponse({"error": f"不支持的文件类型: {ext}"}, status=400)

    file_bytes = up_file.read()
    save_dir = 'uploads'
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, up_file.name)
    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    obj = CorpusData.objects.create(
        fileType=ext,
        original_filename=up_file.name,
        content="解析中...",
        status="解析中"
    )

    def do_sync():
        content = parse_content(ext, file_bytes)
        obj.content = content
        obj.status = "已解析" if not content.startswith("解析失败") else "解析失败"
        obj.save(update_fields=["content", "status"])

    if os.getenv("SYNC_PARSE"):
        do_sync()
    else:
        try:
            parse_corpus_task.delay(obj.id, ext, file_path)
        except Exception:
            do_sync()

    return JsonResponse({
        "message": "已解析(同步)" if obj.status != "解析中" else "已接收, 正在解析",
        "item": {
            "id": obj.id,
            "fileType": obj.fileType,
            "original_filename": obj.original_filename,
            "status": obj.status
        }
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def corpus_detail(request, pk):
    try:
        obj = CorpusData.objects.get(pk=pk)
    except CorpusData.DoesNotExist:
        return JsonResponse({'error': '未找到'}, status=404)
    obj.delete()
    return JsonResponse({'message': '删除成功'})


@require_http_methods(["GET"])
def corpus_data(request):
    query = request.GET.get('query', '').strip()
    file_type = request.GET.get('file_type', '').strip().lower()

    qs = CorpusData.objects.all().order_by('-id')
    if query:
        qs = qs.filter(content__icontains=query)
    if file_type:
        qs = qs.filter(fileType=file_type)

    data = CorpusDataSerializer(qs, many=True).data
    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
def stats(request):
    return JsonResponse(build_stats())
