import os

from apps.data_import.ws_auth import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.urls import path

# Prometheus WS 在线指标
try:
    from prometheus_client import Gauge

    METRIC_WS_ONLINE = Gauge('app_ws_online', 'Current websocket online connections', ['channel', 'ns'])
except Exception:  # noqa
    METRIC_WS_ONLINE = None

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

# 简单占位 Consumer（若项目已有自己的 Consumers，可替换为已有路由）
from channels.generic.websocket import AsyncJsonWebsocketConsumer  # noqa: E402


class NoopConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        # 保持连接，不回显
        pass

    async def disconnect(self, code):
        pass


ws_urlpatterns = [
    path("ws/corpus/", NoopConsumer.as_asgi()),
    path("ws/stats/", NoopConsumer.as_asgi()),
]


class WsMetricsMiddleware:
    """
    统计 WS 在线连接数：
    - 在 websocket.accept 时 +1
    - 在 websocket.disconnect 或异常结束时 -1
    按 channel(Label) = corpus|stats|other，ns(Label)=settings.WS_NAMESPACE 聚合
    """

    def __init__(self, app):
        self.app = app

    def _label_for(self, scope) -> str:
        try:
            path = scope.get("path", "") or ""
            if path.startswith("/ws/corpus/"):
                return "corpus"
            if path.startswith("/ws/stats/"):
                return "stats"
        except Exception:
            pass
        return "other"

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "websocket" or not METRIC_WS_ONLINE:
            return await self.app(scope, receive, send)

        channel = self._label_for(scope)
        ns = getattr(settings, "WS_NAMESPACE", "public")
        online = False

        async def send_wrapper(message):
            nonlocal online
            if message.get("type") == "websocket.accept" and not online:
                online = True
                try:
                    METRIC_WS_ONLINE.labels(channel=channel, ns=ns).inc()
                except Exception:
                    pass
            return await send(message)

        async def receive_wrapper():
            nonlocal online
            msg = await receive()
            if msg.get("type") == "websocket.disconnect" and online:
                try:
                    METRIC_WS_ONLINE.labels(channel=channel, ns=ns).dec()
                except Exception:
                    pass
                online = False
            return msg

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        finally:
            if online:
                try:
                    METRIC_WS_ONLINE.labels(channel=channel, ns=ns).dec()
                except Exception:
                    pass
                online = False


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        WsMetricsMiddleware(
            URLRouter(ws_urlpatterns)
        )
    ),
})
