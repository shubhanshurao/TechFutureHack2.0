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
from Devices.serializers import *
from airflow import *
# Create your views here.


class SetUseCases(APIView):
    def post(self, request, div_id, format=None):
        data = request.data
        try:

            division = Division.objects.get(ID=div_id)
            usecase = UseCases.objects.create(
                Name=data.get('Name'),
                Division=division,
                Active=data.get('Active'),
                Description=data.get('Description')
            )
            return Response({'message': 'UseCases Created Successfully'}, status=status.HTTP_201_CREATED)

        except Division.DoesNotExist:
            return Response({'message': 'Unable to find Division'}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({'message': 'Unable to create Usecase'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, usecase_id, format=None):
        data = request.data
        try:
            usecase = UseCases.objects.get(ID=usecase_id)

            # Update the fields
            usecase.Name = data.get('Name')
            usecase.Active = data.get('Active')
            usecase.Description = data.get('Description')

            # Save the updated object
            usecase.save()

            return Response({'message': 'UseCases updated successfully'}, status=status.HTTP_200_OK)

        except UseCases.DoesNotExist:
            return Response({'message': 'UseCases not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'message': 'Failed to update UseCases', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetUseCaseView(APIView):
    def get(self, request, use_id, format=None):
        try:
            use = UseCases.objects.get(ID=use_id)
            devices = Device.objects.filter(UseCase=use)

            payload = {
                'usecase': UsecaseSerializers(use).data,
                'devices': DeviceSerializer(devices, many=True).data
            }
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response({"message": "some error"}, status=status.HTTP_204_NO_CONTENT)


class ViewUseCases(APIView):
    def get(self, request, div_id, format=None):
        try:
            div = Division.objects.get(ID=div_id)
            usecases = UseCases.objects.filter(Division=div)

            _uses = []
            total = 0
            for use in usecases:
                _uses.append({
                    'details': UsecaseSerializers(use).data,
                    'devices': len(Device.objects.filter(UseCase=use)),
                    'watchers': len(Watcher.objects.filter(Device__UseCase=use)),
                    'alerts': len(Alert.objects.filter(Watcher__Device__UseCase=use))
                })
                total += len(Device.objects.filter(UseCase=use))

            return Response({'usecases': _uses, 'devices': total}, status=status.HTTP_200_OK)

        except Division.DoesNotExist:
            return Response({'message': 'Unable to find Division'}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({'message': 'Unable to View UseCases'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUsecase(APIView):
    def post(self, request, usecase_id):
        try:
            object = UseCases.objects.get(ID=usecase_id)
            object.delete()
            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class CreateDashboardView(APIView):
    def get(self, request, username, usecase_id, format=None):
        use = UseCases.objects.get(ID=usecase_id)
        user = User.objects.get(username=username)

        role = Role.objects.get(User=user)

        patterns = []
        params_ = []
        for dev in Device.objects.filter(UseCase=use):
            patterns.append(dev.Index_pattern)
            params = Param.objects.filter(Device=dev)
            for param in params:
                params_.append(param)

        role_id = UpdateRole(patterns, role.Role_id)

        if use.Dashboard_id and use.Dashboard_link:
            DashboardUpdation(params_, use.ID, use.Dashboard_id)
            dashboard_url = use.Dashboard_link
        else:
            dashboard_url, dashboard_id = DashboardCreation(params_, use.ID)

            use.Dashboard_link = dashboard_url
            use.Dashboard_id = dashboard_id
            use.save(update_fields=['Dashboard_link', 'Dashboard_id'])

        return Response({"embedding": dashboard_url}, status=status.HTTP_200_OK)

# Machine learning


class GetMLOverviewTabView(APIView):
    def get(self, request, usecase_id, format=None):
        usecase = UseCases.objects.get(ID=usecase_id)

        jobs = AirflowJob.objects.filter(Device__UseCase=usecase)
        devices = Device.objects.filter(UseCase=usecase)

        devices_ = []
        for device in devices:
            latest_model = AirflowJob.objects.filter(Status='Completed', Device=device, Type='Training').order_by(
                '-Start_date').first().Name if AirflowJob.objects.filter(Status='Completed', Device=device, Type='Training').exists() else None
            devices_.append({
                'details': DeviceSerializer(device).data,
                'latest_model': latest_model,
                'predictions': len(Prediction.objects.filter(Job__Device=device))
            })

        payload = {
            'jobs': {
                'active': AirflowJobSerializer(jobs.filter(Status='In Progress....'), many=True).data,
                'other': AirflowJobSerializer(jobs.exclude(Status='In Progress....'), many=True).data
            },
            'devices': devices_
        }

        return Response(payload, status=status.HTTP_200_OK)


class GetMLModelsTabView(APIView):
    def get(self, request, usecase_id, format=None):
        usecase = UseCases.objects.get(ID=usecase_id)

        models = MLModel.objects.filter(Job__Device__UseCase=usecase)

        models_ = []
        for model in models:
            predictions = Prediction.objects.filter(Model=model)
            latest_prediction = predictions.order_by(
                '-Created_date').first().Job.Name if predictions.exists() else None
            models_.append({
                'details': MLModelSerializer(model).data,
                'latest_prediction': latest_prediction,
                'prediction_count': len(predictions)
            })

        payload = {
            'models': models_
        }

        return Response(payload, status=status.HTTP_200_OK)


class GetMLPredictionsTabView(APIView):
    def get(self, request, usecase_id, format=None):
        usecase = UseCases.objects.get(ID=usecase_id)

        predictions = Prediction.objects.filter(Job__Device__UseCase=usecase)

        payload = {
            'predictions': PredictionSerializer(predictions, many=True).data
        }

        return Response(payload, status=status.HTTP_200_OK)


class FileMeta(APIView):
    def post(self, request, format=None):
        data = request.data
        print(data)
        try:
            file = FileUpload.objects.create(
                File=data.get('File'),
                Name=data.get('Name'),
                Type=data.get('Type'),
                Size=data.get('Size'),
                Description=data.get('Description')
            )
            return Response({'message': 'File Uploaded Successfully'}, status=status.HTTP_201_CREATED)

        except:
            return Response({'message': 'Unable to Upload File'}, status=status.HTTP_400_BAD_REQUEST)
