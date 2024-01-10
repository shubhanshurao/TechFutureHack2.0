from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('webhook/', ElasticWebhookView.as_view(), name='elastic-webhook'),
    path('anomaly-webhook/', AnomalyWebhookView.as_view(), name='anomaly-webhook'),
    path('data-gap-webhook/', AnomalyMissingDataWebhookView.as_view(), name='data-gap-webhook'),

    path('create-watcher/<str:device_id>/', CreateWatcherView.as_view(), name='create-watcher'),
    path("get-watchers/<str:division_id>/", GetWatchers.as_view(), name="get-watchers"),
    path("add-action/<str:source_type>/<str:source_id>/", AddActionView.as_view(), name='add-action'),
    path("get-users/<str:source_type>/<str:source_id>/", GetUsers.as_view(), name='get-users'),
    path("get-alerts/<str:division_id>/", GetAlerts.as_view(), name='get-alerts'),

    path("create-job/<str:device_id>/", CreateJobView.as_view(), name='create-job'),
    path("update-status/<str:alert_id>/<str:alert_status>/", UpdateStatusView.as_view(), name='update-status'),
    path('create-datagap-watcher/<str:device_id>/', CreateMissingDataJob.as_view(), name='create-datagap-watcher'),
]
