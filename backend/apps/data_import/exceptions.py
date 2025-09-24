# python
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_default_handler

from .responses import fail


class ApiException(Exception):
    def __init__(self, message="业务异常", code=4001, status=400, data=None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.data = data


def drf_exception_handler(exc, context):
    # 先交给 DRF 默认
    response = drf_default_handler(exc, context)
    if response is not None:
        # 规范化已有 DRF 响应
        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            message = detail["detail"]
        else:
            message = detail
        return fail(message=str(message), code=response.status_code, status=response.status_code)
    # 自定义异常
    if isinstance(exc, ApiException):
        return fail(message=str(exc), code=exc.code, status=exc.status, data=exc.data)
    if isinstance(exc, APIException):
        return fail(message=str(exc), code=5001, status=500)
    return None  # 交给中间件兜底


class ApiExceptionMiddleware:
    """
    捕获未处理异常，统一 JSON。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except ApiException as e:
            return JsonResponse({"code": e.code, "message": str(e), "data": e.data}, status=e.status)
        except Http404:
            return JsonResponse({"code": 404, "message": "Not Found", "data": None}, status=404)
        except PermissionDenied:
            return JsonResponse({"code": 403, "message": "Forbidden", "data": None}, status=403)
        except Exception as e:
            if settings.DEBUG:
                raise
            return JsonResponse({"code": 5000, "message": "Server Error", "data": None}, status=500)
