# python
# 文件: `backend/apps/data_import/consumers.py`
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CorpusConsumer(AsyncJsonWebsocketConsumer):
    group_name = "corpus_stream"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def corpus_event(self, event):
        await self.send_json(event["payload"])


class StatsConsumer(AsyncJsonWebsocketConsumer):
    group_name = "global_stats"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def stats_event(self, event):
        await self.send_json(event["payload"])
