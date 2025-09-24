# python
import os

from celery import Celery
from django.conf import settings
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 队列分离
app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default'),
    Queue('parsing'),
    Queue('export'),
    Queue('stats'),
)
app.conf.task_routes = {
    # parsing
    'apps.data_import.tasks.parse_corpus_task': {'queue': 'parsing'},
    # stats
    'apps.data_import.tasks.stats_preaggregate_task': {'queue': 'stats'},
    # export
    'apps.data_import.tasks.export_corpus_start_task': {'queue': 'export'},
    'apps.data_import.tasks.export_corpus_batch_task': {'queue': 'export'},
    'apps.data_import.tasks.export_corpus_finalize_task': {'queue': 'export'},
}

# 定时任务：统计预聚合
app.conf.beat_schedule = {
    'stats-preaggregate-every-30s': {
        'task': 'apps.data_import.tasks.stats_preaggregate_task',
        'schedule': 30.0,
    },
}

# worker 优化与时限
app.conf.worker_prefetch_multiplier = int(os.getenv('CELERY_WORKER_PREFETCH_MULTIPLIER', '4'))
app.conf.task_acks_late = True
app.conf.task_time_limit = getattr(settings, 'CELERY_TASK_TIME_LIMIT', 300)
app.conf.task_soft_time_limit = getattr(settings, 'CELERY_TASK_SOFT_TIME_LIMIT', 280)

# 自动发现任务
app.autodiscover_tasks()
