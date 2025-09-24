# python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

# 强制导入 routing 以便报错更清晰
try:
    import apps.data_import.routing as data_import_routing  # noqa: E402
except ModuleNotFoundError as e:
    raise RuntimeError(
        "无法导入 apps.data_import.routing，请检查:\n"
        "1. 是否存在文件 backend/apps/__init__.py\n"
        "2. 是否在 backend 目录内执行运行命令\n"
        "3. INSTALLED_APPS 中是否包含 'apps.data_import'\n"
        f"原始错误: {e}"
    )

# 使用自定义 Token/JWT 鉴权中间件栈（内部仍保留 Session/AuthMiddlewareStack）
from apps.data_import.ws_auth import TokenAuthMiddlewareStack  # noqa: E402

django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(data_import_routing.websocket_urlpatterns)
    ),
})
