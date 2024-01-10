from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post, PreparedRequest, get
# from .models import *
import json
from Backend.models import *
from .serializers import *
from elastic import *
from Users.serializers import *
from Backend.serializers import *
from Usecases.serializers import *
from Devices.serializers import *
import os
import io
import boto3
from dotenv import load_dotenv
import zipfile
from django.http import HttpResponse

load_dotenv()

# Function to create Certificate for Organiation
def create_CerificateARN(org):
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

    # Initialize IoT client
    iot_client = boto3.client('iot' ,aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_S3_REGION_NAME)  # Replace 'your-region' with your AWS region
    
    # Create a certificate
    cert_response = iot_client.create_keys_and_certificate(setAsActive=True)

    # Attach the policy to the certificate
    policy_name = "PredCo_Device_Policy"
    iot_client.attach_policy(policyName=policy_name, target=cert_response['certificateArn'])

    # Download certificate files
    with open('_deviceCert.pem.crt', 'w') as cert_file:
        cert_file.write(cert_response['certificatePem'])

    with open('_devicePrivateKey.pem.key', 'w') as key_file:
        key_file.write(cert_response['keyPair']['PrivateKey'])

    s3 = boto3.client("s3",aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_S3_REGION_NAME)
    bucket_name = AWS_STORAGE_BUCKET_NAME

    file_path = '_deviceCert.pem.crt'
    file_path_2 = '_devicePrivateKey.pem.key'
    object_key = f'Certificates/org-{org.Name}-{org.ID}/{org.ID}_deviceCert.pem.crt'
    object_key_2 = f'Certificates/org-{org.Name}-{org.ID}/{org.ID}_devicePrivateKey.pem.key'
    
    try:
        s3.upload_file(file_path, bucket_name, object_key)
        print(f'Successfully uploaded {file_path} to {bucket_name}/{object_key}')
    except Exception as e:
        print(f'Error uploading {file_path} to {bucket_name}/{object_key}:{e}')

    try:
        s3.upload_file(file_path_2, bucket_name, object_key_2)
        print(f'Successfully uploaded {file_path_2} to {bucket_name}/{object_key_2}')
    except Exception as e:
        print(f'Error uploading {file_path_2} to {bucket_name}/{object_key_2}:{e}')

    
    return cert_response['certificateArn']

class DownloadMQTTCertificatesView(APIView):
    def get(self, request, org_id):
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
        AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

        s3 = boto3.client('s3' ,aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_S3_REGION_NAME)
        
        org = Organization.objects.get(ID=org_id)

        # Replace 'your_folder_path' with the actual path to your folder in the S3 bucket
        folder_path = f'Certificates/org-{org.Name}-{org.ID}/'

        # Create an in-memory zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
            # List objects in the folder
            response = s3.list_objects(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=folder_path)

            for obj in response.get('Contents', []):
                # Download each file from S3 and add it to the zip file
                file_obj = s3.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=obj['Key'])
                zip_file.writestr(obj['Key'], file_obj['Body'].read())

        # Create the HttpResponse object with the appropriate headers
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{folder_path}.zip"'

        return response

# Create your views here.
class PostOrganizations(APIView):
    def post(self, request, format = None):
        data = request.data
   
        try:
            organization = Organization.objects.create(
                Name = data.get("Name"),
                Website = data.get("Website"),
                Phone_Number = data.get("Phone_Number"),
                Email = data.get("Email"),
            )
            res = IndextemplateCreation(organization.ID)
            organization.Index_template = res
            organization.CertificateARN=create_CerificateARN(organization)
            organization.save(update_fields=['Index_template','CertificateARN'])
            return Response({'message': 'Organization Created Successfully'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'message': "Unable to Create the organization"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, org_id, format = None):
        data = data.request

        try:
            org = Organization.objects.get(ID = org_id)
            org.Name = data.get("Name"),
            org.Phone_Number = data.get("Phone_Number"),
            org.Email = data.get("Email"),

            org.save()

            return Response({'message': 'Organization updated successfully'}, status=status.HTTP_200_OK)
        
        except Organization.DoesNotExist:
            return Response({'message': "Unable to Find the Division"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': 'Failed to update UseCases', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDivision(APIView):
    def post(self, request, org_id, format =None):
        data = request.data
        try:
            
            organization = Organization.objects.filter(ID = org_id)

            if not organization.exists():
               return Response({"message": "something went wrong", 'code': '404'}, status=status.HTTP_404_NOT_FOUND)
            organization = organization.first()
            division = Division.objects.create(
                Name = data.get('Name'),
                Organization  = organization,
                Location = data.get('Location'),
                Description = data.get('Description')
                # add description aswell 
            )
            return Response({'message': 'Division has been created Successfully'}, status=status.HTTP_201_CREATED)
        
        except:
            return Response({'message': "Unable to Create the Division"}, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, div_id, format = None):
        data = data.request

        try:
            div = Division.objects.get(ID = div_id)

            div.Name = data.get('Name'),
            div.Location = data.get('Location'),
            div.Description = data.get('Description')

            div.org()

            return Response({'message': 'Division has been updated Successfully'}, status=status.HTTP_201_CREATED)
        
        except Division.DoesNotExist:
            return Response({'message': "Unable to Find the Division"}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({'message': "Unable to update the Division"}, status=status.HTTP_400_BAD_REQUEST)           


class GetOrganizationsView(APIView):
    def get(self, request, format=None):
        data = request.GET
        organizations = Organization.objects.all()
        serializer = OrganizationSerializers(organizations, many=True).data
        return Response(serializer)


class GetOrganizationView(APIView):
    def get(self, request, org_key):
        try:
            organization = Organization.objects.get(ID = org_key)
            serializer = OrganizationSerializers(organization).data
            return Response(serializer)
        except:
            return Response({'message': 'Error', 'code': '404'}, status=status.HTTP_404_NOT_FOUND)
        

class GetDivisionsView(APIView):
    def get(self, request, org_id): #should org-key not be passed here ?
        try:
            org = Organization.objects.filter(ID = org_id) # org_key = ID
            if not org.exists():
                return Response({'message': 'Error Org not found', 'code': '404'}, status=status.HTTP_404_NOT_FOUND)
            org = org.first() #select the top value
            division = Division.objects.filter(Organization = org)
            data = DivisionSerializers(division, many = True).data
            usecases = UsecaseSerializers(UseCases.objects.filter(Division__Organization=org), many=True).data

            payload = {
                'divisions': data,
                'usecases': usecases,
            }
            
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Error', 'code': '404'}, status=status.HTTP_404_NOT_FOUND)


class DeleteOrganization(APIView):
    def post(self, request, org_id):
        try:
            object = Organization.objects.get(ID = org_id)
            object.delete()
            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class DeleteDivision(APIView):
    def post(self, request, div_id):
        try:
            object = Division.objects.get(ID = div_id)
            object.delete()
            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)

from django.utils import timezone

class GetDashboardView(APIView):
    def get(self, request, division_id, format=None):
        division = Division.objects.filter(ID=division_id)
        division = division.first()
        # watchers = Watcher.objects.filter(Device__UseCase__Division=division)
        alerts = Alert.objects.filter(Watcher__Device__UseCase__Division=division)
        uses = UseCases.objects.filter(Division=division)

        current_year = timezone.now().year
        prev_year = current_year - 1
        counts_by_month = [0] * 12
        counts_by_month_prev = [0] * 12

        for month in range(1, 13):
            
            count = len(Alert.objects.filter(Watcher__Device__UseCase__Division=division, Created_date__year=current_year, Created_date__month__gte=month, Created_date__month__lt=month+1))
            + len(AnomalyAlert.objects.filter(Job__Device__UseCase__Division=division, Created_date__year=current_year, Created_date__month__gte=month, Created_date__month__lt=month+1))
            counts_by_month[month - 1] = count
            
            count = len(Alert.objects.filter(Watcher__Device__UseCase__Division=division, Created_date__year=prev_year, Created_date__month__gte=month, Created_date__month__lt=month+1))
            + len(AnomalyAlert.objects.filter(Job__Device__UseCase__Division=division, Created_date__year=prev_year, Created_date__month__gte=month, Created_date__month__lt=month+1))
            counts_by_month_prev[month - 1] = count

        alerts_usecases = []
        alerts_count = []
        total_alerts = len(alerts) + len(AnomalyAlert.objects.filter(Job__Device__UseCase__Division=division))
        for use in uses:
            alerts_usecases.append(use.Name)
            if(total_alerts != 0):
                alerts_count.append( ((len(Alert.objects.filter(Watcher__Device__UseCase=use))+len(AnomalyAlert.objects.filter(Job__Device__UseCase=use))) / total_alerts) * 100 )
            else:
                alerts_count.append(0)

        payload = {
            'division': DivisionSerializers(division).data,
            'org': OrganizationSerializers(division.Organization).data,
            # 'watchers': WatcherSerializer(watchers, many=True).data,
            'alerts': AlertSerializer(alerts, many=True).data,
            'users': RoleSerializer(Role.objects.filter(Organization=division.Organization), many=True).data,
            'devices': DeviceSerializer(Device.objects.filter(UseCase__Division=division).order_by('Created_date'), many=True).data,
            'usecases': UsecaseSerializers(uses, many=True).data,

            'monthly_alerts': {
                'current': counts_by_month,
                'prev': counts_by_month_prev
            },
            'usecase_wise_alerts': {
                'uses': alerts_usecases,
                'counts': alerts_count
            }
        }

        return Response(payload, status=status.HTTP_200_OK)
