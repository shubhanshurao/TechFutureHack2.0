from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post, PreparedRequest, get
from .models import *
# from .serializers import *
from grafana import *
from airflow import *
from threading import Thread
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from mail import *
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from .serializers import *
from Organization.serializers import OrganizationSerializers
from Users.serializers import RoleSerializer
# Create your views here.

load_dotenv()
# Create your views here.

AWS_REGION = os.getenv('AWS_S3_REGION_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

class CreateTwin(APIView):
    def post(self, request, device_id, format=None):
        data = request.data
        device = Device.objects.get(ID=device_id)
        twin = Twin.objects.create(
            Name=data.get('name'),
            Description=data.get('description'),
            Device=device,
            Files=data.get('files')
        )

        # AWS IoT SiteWise client
        sitewise = boto3.client('iotsitewise', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        
        params = Param.objects.filter(Device=device)
        model_name = device.ID
        model_id = "d0600cda-1bd2-4416-a506-9339a04dbdb1" # create_model(sitewise, model_name, params)

        asset_id = create_asset(sitewise, model_name, model_id)

        # upload to s3
        try:
            # Get the file from the request
            file = request.FILES['file']

            # Set up the S3 client
            s3 = boto3.client('s3', region_name=AWS_REGION,
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            # Generate a unique file name (you may want to implement your own logic)
            file_name = f"org_{device.UseCase.Division.Organization.Name}_{device.UseCase.Division.Organization.ID}/usecase_{device.UseCase.Name}_{device.UseCase.ID}/{device.ID}_{datetime.now().strftime('%d-%B-%Y-%H:%M')}_{str(file)}"
            # Upload the file to S3
            s3.upload_fileobj(file, s3_bucket_name, file_name)

        except Exception as e:
            print(str(e))

        # Make rules
        rules = {}
        color_ind = 0
        colors = []
        for watcher in Watcher.objects.filter(Device=device):
            params = watcher.Params.split(',')
            conditions = watcher.Conditions.split(',')
            thresholds = watcher.Thresholds.split(',')
            
            for i in range(len(params)):
                rules[params[i]] = []
                rules[params[i]].append({
                    'condition': f"{params[i]} {conditions[i]} {thresholds[i]}",
                    'color': colors[color_ind]
                })
                color_ind += 1

        # Trigger airflow dag
        params = [param.Doc_field for param in params]

        org = device.UseCase.Division.Organization
        config = {
            'twin_name': twin.Name, #
            'twin_file_name': file_name, #
            'twin_id': twin.ID, #

            'rules': rules, #
            'org_path': f"Org_{org.Name}_{org.ID}/UseCase_{device.UseCase.Name}_{device.UseCase.ID}",#
            
            'asset_id': asset_id, #
            'workspace_id': ExtraKey.objects.get(Model_type='organization', Model_id=org.ID, Key_type='workspace_id'), #
            'model_id': model_id,#

            'params': params, 
            'workspace_key': ExtraKey.objects.get(Model_type='organization', Model_id=org.ID, Key_type='workspace_key'),
            'datasource_uid': ExtraKey.objects.get(Model_type='organization', Model_id=org.ID, Key_type='datasource_uid'),
            'folder_uid': ExtraKey.objects.get(Model_type='usecase', Model_id=device.UseCase.ID, Key_type='folder_uid'),
        }

        t = Thread(target=send_airflow_request, args=[device, twin.ID, "create_digital_twin_dag", "twin", False, config])
        t.start()

        return Response({"message": "Twin generation started."}, status=status.HTTP_200_OK)

class GetTwin(APIView):
    def get(self, request, twin_id, format=None):
        twin = Twin.objects.get(ID=twin_id)
        params = Param.objects.filter(Device=twin.Device)

        try:
            url = ExtraKey.objects.get(Model_type='twin', Model_id=twin_id, Key_type='grafana_url').Key_value
        except:
            url = ""

        payload = {
            'twin': TwinSerializer(twin).data,
            'params': ParamSerializer(params, many=True).data,
            'dashboard_url': url
        }

        return Response(payload, status=status.HTTP_200_OK)

class GetUsecases(APIView):
    def get(self, request, org_id, format=None):
        uses = UseCases.objects.filter(Division__Organization__ID=org_id)
        _uses = []
        for use in uses:
            _uses.append({
                'details': UsecaseSerializers(use).data,
                'devices': len(Device.objects.filter(UseCase=use))
            })

        return Response({'usecases': _uses}, status=status.HTTP_200_OK)


@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class TwinCreated(APIView):
    def post(self, request, format=None):
        data = request.data 
        Authoization = request.headers.get('Authoization')
        status = data.get('status')

        twin = Twin.objects.filter(ID=Authoization)
        if twin.exists():
            if status == 'Completed':
                dashboard_url = data.get("dashboard_url")
                ExtraKey.objects.create(
                    Model_type="twin",
                    Model_id=Authoization,
                    Key_type="grafana_url",
                    Key_value=dashboard_url
                )
                return Response({"message": "Done"}, status=status.HTTP_200_OK)
            else :
                twin = twin.first()

                twin.Active = False
                twin.Completed = False
                twin.save()
                return Response({"message": "Done"}, status=status.HTTP_200_OK)
        return Response({"message": "Twin doesn't exist"}, status=status.HTTP_200_OK)

class GetTwins(APIView):
    def get(self, request, usecase_id, format=None):
        usecase = UseCases.objects.get(ID=usecase_id)
        twins = Twin.objects.filter(Device__UseCase=usecase)

        twins_ = []
        for twin in twins:
            try:
                url = ExtraKey.objects.get(Model_type='twin', Model_id=twin.ID, Key_type='grafana_url').Key_value
            except:
                url = ""
            twins_.append({
                'details': TwinSerializer(twin).data,
                'url': url
            })

        payload = {
            'twins': twins_
        }
        return Response(payload, status=status.HTTP_200_OK)

class GetTwinDashboard(APIView):
    def get(self, request, usecase_id, format=None):
        usecase = UseCases.objects.get(ID=usecase_id)
        devices = Device.objects.filter(UseCase=usecase)
        org = usecase.Division.Organization
        
        payload = {
            'usecase': UsecaseSerializers(usecase).data,
            'users': RoleSerializer(Role.objects.filter(Organization__ID=org.ID), many=True).data,
            'devices': DeviceSerializer(devices, many=True).data,
            'alerts': AlertSerializer(Alert.objects.filter(Watcher__Device__UseCase=usecase), many=True).data,
            'twin_count': len(Twin.objects.filter(Device__UseCase=usecase))
        }
        return Response(payload, status=status.HTTP_200_OK)
