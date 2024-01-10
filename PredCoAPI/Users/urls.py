from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('create-user/<str:org_id>/', CreateUser.as_view(), name='Create User'),
    path('delete-user/<str:user_id>/', DeleteUser.as_view(), name='Delete User'),
    path('Update-profile/<str:user_id>/',
         UpdateProfile.as_view(), name='Update Profile'),
    path('view-users/<str:org_id>/', ViewUsers.as_view(), name='View Users'),
    path('view-user/<str:user_id>/', ViewUser.as_view(), name='View User'),
    path('get-my-org/<str:username>/',
         GetMyOrganization.as_view(), name='get org'),
    path('view-profile-details/<str:username>/',
         GetProfileDetails.as_view(), name='Get the profile details'),
    path('get-api-key/<str:username>/',
         GetAPIKeyView.as_view(), name='get-api-key'),
    path('generate-api-key/<str:username>/',
         GenerateAPIKey.as_view(), name='generate-api-key'),
    path('push-notifications/<str:username>/', EnableUserNotification.as_view(), name='user-notification')
]
