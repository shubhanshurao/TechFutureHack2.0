from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # path('startup/create-product/', CreateProductView.as_view()),
    path('setup_organizations/', PostOrganizations.as_view(), name="Organization_add"),
    path('setup_division/<str:org_id>/', PostDivision.as_view(), name='Setting up division'),
    path('view-organizations/', GetOrganizationsView.as_view(), name =  'list of Organisations'),
    path('view-organization/<str:org_key>/', GetOrganizationView.as_view(), name = 'OrganizationDetails'),
    path('view-division/<str:org_id>/', GetDivisionsView.as_view(), name = 'listof Divisions'),
    path('delete_organization/<str:org_id>', DeleteOrganization.as_view(), name = 'Delete Organization'),
    path('delete_division/<str:div_id>', DeleteDivision.as_view(), name = 'Delete division'),
    path('get-dashboard/<str:division_id>', GetDashboardView.as_view(), name='get-division'),

    path('download-certificates/<str:org_id>', DownloadMQTTCertificatesView.as_view(), name='download-certs')
]
