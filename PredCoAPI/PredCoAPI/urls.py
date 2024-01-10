"""PredCoAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

# keep the first lphabet of each app capital
urlpatterns = [
    path('admin/', admin.site.urls),
    path('Backend/', include('Backend.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    # path('Sensor/', include('Sensor.urls')),
    path('Organization/', include('Organization.urls')),
    path('Usecases/', include('Usecases.urls')),
    path('Devices/', include('Devices.urls')),
    path('Users/', include('Users.urls')),
    path('Alerts/', include('Alerts.urls')),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('Onboarding/', include('JoinReq.urls')),
    path('Digital-Twin/', include('DigitalTwin.urls')),

]
