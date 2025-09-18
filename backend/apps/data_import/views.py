import os

from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CorpusData  # 假设语料数据存储在CorpusData模型中


@csrf_exempt
def upload_data(request):
    if request.method == "POST" and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = file.name
        file_path = os.path.join('uploads', file_name)

        # Save the file to a location on the server
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # You can add more logic here to parse and analyze the uploaded file

        return JsonResponse({"message": f"File {file_name} uploaded successfully"})
    return JsonResponse({"error": "No file provided"}, status=400)


def corpus_data(request):
    query = request.GET.get('query', '')  # 获取搜索关键字
    file_type = request.GET.get('file_type', '')  # 获取文件类型筛选

    # 根据搜索和筛选条件查询语料数据
    data = CorpusData.objects.all()
    if query:
        data = data.filter(content__icontains=query)  # 根据内容搜索
    if file_type:
        data = data.filter(fileType=file_type)  # 根据文件类型筛选

    # 返回符合条件的数据
    result = list(data.values('id', 'fileType', 'content', 'status'))  # 返回需要的字段
    return JsonResponse(result, safe=False)
