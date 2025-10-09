# backend/apps/data_import/middleware.py
import logging


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        # 可以在这里添加自定义日志上下文字段
        record.request_id = getattr(record, "request_id", "-")
        record.path = getattr(record, "path", "-")
        record.method = getattr(record, "method", "-")
        record.status_code = getattr(record, "status_code", "-")
        record.user_id = getattr(record, "user_id", "-")
        return True


# python
class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 可以在这里生成/设置 request_id
        response = self.get_response(request)
        return response
