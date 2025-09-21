# python
# 文件: backend/config/asgi.py
import os
import sys
from pathlib import Path

# 确保把 backend 根目录加入 sys.path （本文件在 backend/config/）
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 确保 apps 是包：需要存在 backend/apps/__init__.py

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402

# 强制在这里导入 routing，失败时给出明确错误
try:
    import apps.data_import.routing as data_import_routing  # noqa: E402
except ModuleNotFoundError as e:
    raise RuntimeError(
        "无法导入 apps.data_import.routing，请检查:\n"
        "1. 是否存在文件 backend/apps/__init__.py\n"
        "2. 是否在 backend 目录内执行运行命令 (例如: uvicorn config.asgi:application --reload)\n"
        "3. INSTALLED_APPS 中是否包含 'apps.data_import'\n"
        f"原始错误: {e}"
    )

django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(data_import_routing.websocket_urlpatterns)
    ),
})
