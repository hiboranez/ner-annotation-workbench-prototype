# python
from django.apps import AppConfig


class DataImportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_import'

    def ready(self):
        # 确保信号注册
        from . import signals  # noqa
