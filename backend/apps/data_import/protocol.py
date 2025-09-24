# python
import time
import uuid
from typing import Any, Dict, Optional


def now_ms() -> int:
    return int(time.time() * 1000)


def make_event(event: str,
               data: Optional[Dict[str, Any]] = None,
               *,
               version: int = 1,
               trace_id: Optional[str] = None,
               extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """统一事件协议封装"""
    payload = {
        "version": version,
        "event": event,
        "data": data or {},
        "ts": now_ms(),
        "trace_id": trace_id or uuid.uuid4().hex,
    }
    if extra:
        payload.update(extra)
    return payload
