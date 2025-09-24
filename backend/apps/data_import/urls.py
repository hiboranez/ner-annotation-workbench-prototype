from django.urls import path

from .views import stats_view, corpus_list, corpus_delete, cache_refresh_view, upload_view

app_name = "data_import"

urlpatterns = [
    path("stats/", stats_view, name="stats"),
    path("corpus-data/", corpus_list, name="corpus-list"),
    path("corpus-data/<int:pk>/", corpus_delete, name="corpus-delete"),
    path("cache/refresh/", cache_refresh_view, name="cache-refresh"),
    path("upload/", upload_view, name="upload"),
]
