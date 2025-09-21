# python
# 文件: `backend/apps/data_import/routing.py`
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/corpus/", consumers.CorpusConsumer.as_asgi()),
    path("ws/stats/", consumers.StatsConsumer.as_asgi()),
]
