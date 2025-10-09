import os

from celery import Celery
from celery.signals import worker_ready

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_ready.connect
def _start_prometheus_exporter(sender=None, **kwargs):
    """
    可选：在 Celery Worker 中启动 Prometheus Exporter。
    设置环境变量 CELERY_METRICS_PORT=9095（或其他端口）生效。
    注意：多进程/多实例需为每个 worker 使用不同端口，或改为普罗米修斯多进程模式。
    """
    port_s = os.getenv("CELERY_METRICS_PORT", "")
    if not port_s:
        return
    try:
        port = int(port_s)
        if port > 0:
            from prometheus_client import start_http_server
            start_http_server(port)
    except Exception:
        pass
