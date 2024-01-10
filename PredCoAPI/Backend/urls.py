from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('save-device-token/', SaveDeviceToken.as_view(), name='Subscribe-Device'),
]


