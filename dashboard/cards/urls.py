from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/task/update/', views.api_task_update, name='api_task_update'),
    path('api/check/', views.api_check_host, name='api_check_host'),
]
