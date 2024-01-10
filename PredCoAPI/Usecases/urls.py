from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('set-usecases/<str:div_id>/',
         SetUseCases.as_view(), name='setting Usecases'),
    path('view-usecases/<str:div_id>/',
         ViewUseCases.as_view(), name='view usecases'),
    # path('set-machines/<str:use_case_id>/', SetupMachines.as_view(), name = 'Setup Machines'),
    # path('view-machines/<str:usecase_id>/', ViewMachines.as_view(), name = 'View Machines'),
    path('delete-usecase/<str:usecase_id>/',
         DeleteUsecase.as_view(), name='View Machines'),

    path('create-dashboard/<str:username>/<str:usecase_id>/',
         CreateDashboardView.as_view(), name='create-dashboard'),
    # path('delete-machines/<str:mach_id>/', DeleteMachine.as_view(), name = 'View Machines'),
    path('get-usecase/<str:use_id>/',
         GetUseCaseView.as_view(), name='get-usecase'),

    path('ml-overview-tab/<str:usecase_id>/',
         GetMLOverviewTabView.as_view(), name='ml-overview-tab'),
    path('ml-models-tab/<str:usecase_id>/',
         GetMLModelsTabView.as_view(), name='ml-models-tab'),
    path('ml-predictions-tab/<str:usecase_id>/',
         GetMLPredictionsTabView.as_view(), name='ml-predictions-tab'),
    path('file-upload-meta/', FileMeta.as_view(), name='file-upload-meta'),
]
