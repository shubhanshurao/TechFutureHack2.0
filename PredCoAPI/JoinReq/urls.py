from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('submit-details/', OnboardingForm.as_view(), name='OnBoarding View'),
    path('on-boarding-status/<str:org_id>/<str:api_key>', OnboardingStatus.as_view(), name = 'OnBoarding Status'),
    path('verify-otp/<str:username>/', VerifyOTP.as_view(), name='Verify otp'),
]