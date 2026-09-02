from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Prometheus /metrics
    path('', include('django_prometheus.urls')),

    path('admin/', admin.site.urls),
    path('api/data-import/', include('apps.data_import.urls')),
    path('api/data-import/sync/', include('apps.data_import.urls_sync')),
    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
