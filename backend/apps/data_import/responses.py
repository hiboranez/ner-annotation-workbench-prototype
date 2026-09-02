# python
from rest_framework.response import Response


def ok(data=None, message="OK", code=0, status=200, **extra):
    payload = {"code": code, "message": message, "data": data}
    if extra:
        payload.update(extra)
    return Response(payload, status=status)


def fail(message="失败", code=4000, status=400, data=None):
    return Response({"code": code, "message": message, "data": data}, status=status)
