from django.http import JsonResponse

def index(request):
    return JsonResponse({"page": "数据导入 API 正常运行"})
