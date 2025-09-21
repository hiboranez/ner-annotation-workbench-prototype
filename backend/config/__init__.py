# python
# 文件: `backend/config/__init__.py` 末尾追加
from .celery import app as celery_app

__all__ = ("celery_app",)
