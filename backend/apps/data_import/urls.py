from django.urls import path

from . import views

urlpatterns = [
    path('upload/', views.upload_data, name='upload_data'),
    path('corpus-data/', views.corpus_data, name='corpus_data'),
    path('stats/', views.stats, name='stats'),
]
