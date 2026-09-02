# python
from django.urls import path

from .views_sync import sync_after

app_name = "data_import_sync"

urlpatterns = [
    path("after/", sync_after, name="sync-after"),
]
