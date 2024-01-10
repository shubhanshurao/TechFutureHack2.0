from django.urls import path
from .views import *
from django.conf import settings

urlpatterns = [
    path('get-twins/<str:usecase_id>/', GetTwins.as_view(), name = 'get-twins'),
    path('get-usecases/<str:org_id>/', GetUsecases.as_view(), name = 'get-usecases'),
    path('create-twin/<str:device_id>/', CreateTwin.as_view(), name = 'create-twin'),
    path('get-dashboard/<str:usecase_id>/', GetTwinDashboard.as_view(), name = 'get-dashboard'),
    path('get-twin/<str:twin_id>/', GetTwin.as_view(), name = 'get-twin'),

    path('twin-created/', TwinCreated.as_view(), name = 'twin-created'),
]