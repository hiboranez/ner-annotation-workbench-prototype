# python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/data-import/', include('apps.data_import.urls')),
    # 增量同步接口分支：/api/data-import/sync/after
    path('api/data-import/sync/', include('apps.data_import.urls_sync')),
    path("api/data-overview/", include("apps.data_overview.urls")),
    path("api/data-annotation/", include("apps.data_annotation.urls")),
    path("api/data-export/", include("apps.data_export.urls")),
]
