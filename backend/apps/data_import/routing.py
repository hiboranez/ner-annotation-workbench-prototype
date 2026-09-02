from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.urls import path


class NoopConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        pass

    async def disconnect(self, code):
        pass


websocket_urlpatterns = [
    path("ws/corpus/", NoopConsumer.as_asgi()),
    path("ws/stats/", NoopConsumer.as_asgi()),
]
