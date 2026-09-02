# python
import time
from collections import deque
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from .protocol import make_event


class BaseJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """通用基类：鉴权校验、命名空间、过滤、简单节流、统一协议封装。"""

    group_names = []  # 子类填充
    allow_anonymous_in_debug = True

    def _parse_query(self):
        raw_qs = self.scope.get("query_string", b"")
        try:
            qs = parse_qs(raw_qs.decode())
        except Exception:
            qs = {}
        # 命名空间与过滤
        self.ns = (qs.get("ns", [settings.WS_NAMESPACE])[0] or settings.WS_NAMESPACE).strip()
        self.filter_file_type = (qs.get("file_type", [""])[0] or "").strip().lower()
        self.filter_search = (qs.get("search", [""])[0] or "").strip()
        # 节流参数
        self.max_send_per_sec = max(1, int(getattr(settings, "WS_MAX_SEND_PER_SEC", 25)))
        self._sent_times = deque()  # 存最近 1s 的发送时间戳

    async def connect(self):
        self._parse_query()
        auth_ok = bool(self.scope.get("auth_ok"))
        # 严格模式：生产环境建议设置 WS_SHARED_TOKEN 或 JWT，并将 DEBUG 置 0
        if not auth_ok and not (self.allow_anonymous_in_debug and settings.DEBUG):
            await self.close(code=4401)
            return

        await self.accept()
        # 订阅分组（子类定义）
        for g in self.group_names:
            await self.channel_layer.group_add(g, self.channel_name)

        # 可选：握手事件
        await self.send_json(make_event(
            event="ws.connected",
            data={"ns": self.ns},
        ))

    async def disconnect(self, code):
        for g in self.group_names:
            try:
                await self.channel_layer.group_discard(g, self.channel_name)
            except Exception:
                pass

    def _should_throttle(self) -> bool:
        now = time.time()
        window_start = now - 1.0
        while self._sent_times and self._sent_times[0] < window_start:
            self._sent_times.popleft()
        if len(self._sent_times) >= self.max_send_per_sec:
            return True
        self._sent_times.append(now)
        return False

    async def push_event(self, event: str, data: dict):
        """统一协议封装 + 节流"""
        if self._should_throttle():
            # 被节流时，尽量少打扰客户端；可以扩展上报 throttle 事件
            return
        await self.send_json(make_event(event=event, data=data, extra={"ns": self.ns}))


class CorpusConsumer(BaseJsonWebsocketConsumer):
    group_names = ["corpus_stream"]

    async def corpus_event(self, event):
        payload = event.get("payload", {})  # 由 signals 广播
        ev = payload.get("event") or "corpus.unknown"
        data = payload.get("data") or {}

        # 过滤：file_type
        if self.filter_file_type and data.get("fileType", "").lower() != self.filter_file_type:
            return
        # 过滤：search（仅当 content 可见时）
        if self.filter_search:
            content = data.get("content", "")
            # 若消息无 content，跳过过滤以避免漏报补全
            if content and (self.filter_search.lower() not in content.lower()):
                return

        await self.push_event(ev, data)


class StatsConsumer(BaseJsonWebsocketConsumer):
    group_names = ["global_stats"]

    async def stats_event(self, event):
        payload = event.get("payload", {})
        ev = payload.get("event") or "stats.update"
        data = payload.get("stats") or payload.get("data") or {}
        await self.push_event(ev, data)
