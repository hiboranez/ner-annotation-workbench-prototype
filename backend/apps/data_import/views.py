import json
import os
from io import BytesIO

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CorpusData
from .serializers import CorpusDataSerializer

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'json'}


def extract_pdf_text(file_bytes, limit=10000):
    try:
        import PyPDF2
    except ImportError:
        return "解析失败：缺少 PyPDF2，请安装后重试"
    try:
        if not file_bytes:
            return "解析失败：文件内容为空"
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")  # 尝试空密码
            except Exception:
                return "解析失败：PDF已加密"
        text_parts = []
        total = 0
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt:
                txt = txt.strip()
                if not txt:
                    continue
                remain = limit - total
                if remain <= 0:
                    break
                if len(txt) > remain:
                    txt = txt[:remain]
                text_parts.append(txt)
                total += len(txt)
            if total >= limit:
                break
        content = "\n".join(text_parts).strip() or "解析结果为空"
        return content[:limit]
    except Exception as e:
        return f"解析失败：{e}"


def extract_docx_text(file_bytes, limit=10000):
    try:
        from docx import Document
    except ImportError:
        return "解析失败：缺少 python-docx，请安装后重试"
    try:
        if not file_bytes:
            return "解析失败：文件内容为空"
        doc = Document(BytesIO(file_bytes))
        parts = []
        total = 0
        for p in doc.paragraphs:
            t = (p.text or "").strip()
            if not t:
                continue
            remain = limit - total
            if remain <= 0:
                break
            if len(t) > remain:
                t = t[:remain]
            parts.append(t)
            total += len(t)
        content = "\n".join(parts).strip() or "解析结果为空"
        return content[:limit]
    except Exception as e:
        return f"解析失败：{e}"


@csrf_exempt
@require_http_methods(["POST"])
def upload_data(request):
    up_file = request.FILES.get('file')
    if not up_file:
        return JsonResponse({"error": "缺少文件"}, status=400)

    ext = up_file.name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        return JsonResponse({"error": f"不支持的文件类型: {ext}"}, status=400)

    # 一次性读取字节，避免后续解析读到不完整文件
    file_bytes = up_file.read()

    # 先保存原文件
    save_dir = 'uploads'
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, up_file.name)
    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    try:
        if ext == 'txt':
            content = file_bytes.decode(errors='ignore')[:10000]
        elif ext == 'json':
            raw = file_bytes.decode(errors='ignore')
            try:
                parsed = json.loads(raw)
                content = json.dumps(parsed, ensure_ascii=False)[:10000]
            except Exception:
                content = raw[:10000]
        elif ext == 'pdf':
            content = extract_pdf_text(file_bytes)
        elif ext == 'docx':
            content = extract_docx_text(file_bytes)
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


@csrf_exempt
@require_http_methods(["DELETE"])
def corpus_detail(request, pk):
    try:
        obj = CorpusData.objects.get(pk=pk)
    except CorpusData.DoesNotExist:
        return JsonResponse({'error': '未找到'}, status=404)
    obj.delete()
    return JsonResponse({'message': '删除成功'})


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
