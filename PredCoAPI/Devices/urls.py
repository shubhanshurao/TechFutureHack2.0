from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('setup-devices/<str:usecase_id>/', SetupDevices.as_view(), name = 'Setup devices'),
    path('view-devices/<str:usecase_id>/', ViewDevices.as_view(), name='View Devices'),
    path('get-unique-key/<str:device_id>/', UniqueKeyDetail.as_view(), name = 'Get Unique Key'),
    path('delete-devices/<str:device_id>/', DeleteDevice.as_view(), name = 'Delete Machines'),
    path('set-param/<str:device_id>/', SetParams.as_view(), name='Setup Param'),
    path('get-device/<str:device_id>/', GetDevice.as_view(), name='get-device'),
    path('get-params/<str:device_id>/', GetParams.as_view(), name='get-params'),
    path('get-actions/<str:device_id>/', GetActions.as_view(), name='get-actions'),

    path('update-param/<str:param_id>/', UpdateParam.as_view(), name='update-param'),
    path('airflow/train-model/<str:device_id>/', TrainModel.as_view(), name='train-model'),
    path('airflow/forecast/<str:device_id>/', Forecast.as_view(), name='forecast'),
    path('airflow/update-job/', JobCompletion.as_view(), name='Job Complete'),

    path('airflow/get-predictions/<str:device_id>/', GetPreviousPredictions.as_view(), name='previous-predictions'),
    path('airflow/get-prediction/<str:prediction_id>/', GetPredictionView.as_view(), name='get-prediction'),

    path('ml/get-models/<str:device_id>', GetAvailableModels.as_view(), name='get-models'),
    path('talkback/<str:device_id>/<str:action>', Talkback.as_view(), name="Talkback function"),

    path('ml/detect-pattern/<str:device_id>/', DetectPattern.as_view(), name='detect-pattern'),
    path('ml/pattern-detected/', PatternDetectionCompletedView.as_view(), name='pattern-detected'),

    path('post-device-data/<str:device_id>/', PostData.as_view(), name='Post Device Data'),
]