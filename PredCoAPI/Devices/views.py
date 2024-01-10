from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post, PreparedRequest, get
# from .models import *
import json
from Backend.models import *
from .serializers import *
from elastic import *
from airflow import *
from paho.mqtt import client as mqtt_client
import json
from time import sleep
from threading import Thread
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from mail import *
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
# Create your views here.

load_dotenv()


class SetupDevices(APIView):
    def post(self, request, usecase_id, format=None):
        data = request.data
        try:
            useCase = UseCases.objects.get(ID=usecase_id)
            device = Device.objects.create(
                Name=data.get('Name'),
                Active=data.get('Active'),
                Description=data.get('Description'),
                UseCase=useCase
            )
            # elastic
            res, view_id = IndexPatternCreation(device.ID)
            # print(res)
            device.Index_pattern = res
            device.Data_view_id = view_id
            device.save(update_fields=['Index_pattern', 'Data_view_id'])
            t = Thread(target=send_iot_airflow_request, args=[
                       device, useCase.Division.Organization, "init_device_dag"])
            t.start()

            # elastic
            return Response({'message': 'Device Added Successfully'}, status=status.HTTP_201_CREATED)

        except UseCases.DoesNotExist:
            return Response({'message': 'UseCase not found'}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({'message': 'Unable to Create Machines'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, dev_id, format=None):
        data = data.request

        try:
            dev = Device.objects.get(ID=dev_id)

            dev.Name = data.get('Name'),
            dev.Active = data.get('Active'),
            dev.Description = data.get('Description')

            dev.save()

            return Response({'message': 'Organization updated successfully'}, status=status.HTTP_200_OK)

        except Device.DoesNotExist:
            return Response({'message': "Unable to Find the Device"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': 'Failed to update UseCases', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewDevices(APIView):
    def get(self, requst, usecase_id, format=None):
        try:
            usecase = UseCases.objects.get(ID=usecase_id)
            devices = Device.objects.filter(UseCase=usecase)
            devices_ = []
            for dev in devices:
                devices_.append({
                    'details': DeviceSerializer(dev).data,
                    'params': ParamSerializer(Param.objects.filter(Device=dev), many=True).data
                })

            return Response({'devices': devices_}, status=status.HTTP_200_OK)

        except UseCases.DoesNotExist:
            return Response({'message': 'UseCase not found'}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({'message': 'Unable to fetch Machines'}, status=status.HTTP_400_BAD_REQUEST)


class GetParams(APIView):
    def get(self, request, device_id, format=None):
        device = Device.objects.get(ID=device_id)
        params = Param.objects.filter(Device=device)

        params_ = []
        for param in params:
            detector = PatternDetector.objects.filter(Param=param)
            params_.append({
                'details': ParamSerializer(param).data,
                'patterns': detector.first().Patterns.split(',') if detector.exists() else []
            })

        payload = {
            'params': params_
        }
        return Response(payload, status=status.HTTP_200_OK)


class GetActions(APIView):
    def get(self, request, device_id, format=None):
        actions = Action.objects.filter(Type='Device', Misc_id=device_id)

        return Response(ActionSerializer(actions, many=True).data, status=status.HTTP_200_OK)


class GetDevice(APIView):
    def get(self, request, device_id, format=None):
        device = Device.objects.get(ID=device_id)
        params = Param.objects.filter(Device=device)

        payload = {
            'device': DeviceSerializer(device).data,
        }
        return Response(payload, status=status.HTTP_200_OK)


class UniqueKeyDetail(APIView):
    def get(self, request, device_id, format=None):
        try:
            device = Device.objects.get(ID=device_id)
            return Response({'unique_key': device.Unique_Key})
        except Device.DoesNotExist:
            return Response({'message': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)


class SetParams(APIView):
    def post(self, request, device_id, format=None):
        data = request.data
        try:
            dev = Device.objects.get(ID=device_id)
            param = Param.objects.create(
                Name=data.get('Name'),
                DataType=data.get('Type'),
                Device=dev,
                Doc_field=data.get('Doc_field'),
                Chart_type=data.get('Chart_type'),
            )
            return Response({'message': 'Param Setup Successfully'}, status=status.HTTP_201_CREATED)
        except Device.DoesNotExist:
            return Response({'message': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'Unable to Create Param'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateParam(APIView):
    def put(self, request, param_id):
        data = request.data
        param = Param.objects.get(ID=param_id)

        param.Name = data.get('Name')
        param.DataType = data.get('Type')
        param.Doc_field = data.get('Doc_field')
        param.Chart_type = data.get('Chart_type')

        param.save(update_fields=['Name', 'DataType',
                   'Doc_field', 'Chart_type'])

        patterns = data.get('Patterns', [])
        if len(patterns) > 0:
            if not PatternDetector.objects.filter(Param__Device=param.Device).exists():
                StartAbnormalPatternDetectorWatcher(param.Device)
            detector = PatternDetector.objects.filter(Param__ID=param_id)
            if detector.exists():
                detector = detector.first()

                detector.Patterns = ",".join(patterns)
                detector.save(update_fields=['Patterns'])

            param = Param.objects.get(ID=param_id)
            detector = PatternDetector.objects.create(
                Param=param, Patterns=",".join(patterns))

        return Response({"message": "updated"}, status=status.HTTP_200_OK)


class DeleteDevice(APIView):
    def post(self, request, device_id):
        try:
            object = Device.objects.get(ID=device_id)
            object.delete()
            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


# Machine learning


class GetPreviousPredictions(APIView):
    def get(self, request, device_id, format=None):
        device = Device.objects.get(ID=device_id)

        predictions = Prediction.objects.filter(Job__Device=device)
        predictions_ = []
        for prediction in predictions:
            predictions_.append({
                'meta': PredictionSerializer(prediction).data,
                'predictions': get_predictions(prediction.File_name)
            })

        return Response({'predictions': predictions_}, status=status.HTTP_200_OK)


class TrainModel(APIView):
    def post(self, request, device_id):
        data = request.data
        try:
            model_type = data.get('model_type')
            username = data.get('username')
            user = User.objects.get(username=username)

            device = Device.objects.get(ID=device_id)
            aggr_cols = []
            for param in Param.objects.filter(Device=device):
                aggr_cols.append('"{}"'.format(param.Doc_field))

            months_to_subtract = data.get('months_back')
            current_date = datetime.now()
            months_ago = current_date - \
                timedelta(days=30*int(months_to_subtract))

            if model_type == "lstm":
                job = AirflowJob.objects.create(Name=data.get(
                    'name'), Device=device, Type='Training', Started_by=user, Dag_id='forecast_train_dag')

                config = {
                    "n_input": data.get('n_input'),
                    "aggr_cols": ",".join(aggr_cols),
                    "filter_date": months_ago.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                }

                t2 = Thread(target=send_airflow_request, args=[
                            device, job.ID, job.Dag_id, 'lstm', True, config])
                t2.start()

            else:
                job = AirflowJob.objects.create(Name=data.get(
                    'name'), Device=device, Type='Training', Started_by=user, Dag_id='ann_train_dag')

                config = {
                    "aggr_cols": ",".join(aggr_cols),
                    "filter_date": months_ago.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                }

                t3 = Thread(target=send_ann_airflow_request, args=[
                            device, job.ID, job.Dag_id, True, config])
                t3.start()

            return Response({'message': 'Training job started succesfully!'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class Forecast(APIView):
    def post(self, request, device_id):
        data = request.data
        try:
            model_type = data.get('model_type')
            username = request.data.get('username')
            user = User.objects.get(username=username)

            device = Device.objects.get(ID=device_id)

            model = MLModel.objects.get(ID=data.get('model'))
            col_order = []
            for col in model.Column_order.split(',') if model.Column_order else []:
                col_order.append('"{}"'.format(col))

            if model_type == "lstm":

                job = AirflowJob.objects.create(Name=data.get(
                    'name'), Device=device, Type='Prediction', Started_by=user, Dag_id='forecast_predict_dag')

                config = {
                    "aggr_cols": ",".join(col_order),
                    "n_input": model.N_input,
                    "prediction_size": data.get('prediction_size'),
                    "model_file_name": model.File_name
                }

                t1 = Thread(target=send_airflow_request, args=[
                            device, job.ID, job.Dag_id, 'lstm', False, config])

            else:

                job = AirflowJob.objects.create(Name=data.get(
                    'name'), Device=device, Type='Prediction', Started_by=user, Dag_id='ann_predict_dag')

                prediction_type = data.get('prediction_type')
                if prediction_type == "single":

                    date = datetime.fromisoformat(data.get('start_date'))

                    config = {
                        "col_order": ",".join(col_order),
                        "prediction_type": prediction_type,
                        "model_file_name": model.File_name,
                        "recieved_date": date.strftime('%Y-%m-%d %H:%M'),
                    }

                    t1 = Thread(target=send_ann_airflow_request, args=[
                                device, job.ID, job.Dag_id, False, config])

                else:

                    start_date = datetime.fromisoformat(data.get('start_date'))
                    end_date = datetime.fromisoformat(data.get('end_date'))

                    config = {
                        "col_order": ",".join(col_order),
                        "prediction_type": prediction_type,
                        "model_file_name": model.File_name,
                        "start_datetime": start_date.strftime('%Y-%m-%d %H:%M'),
                        "end_datetime": end_date.strftime('%Y-%m-%d %H:%M'),
                    }

                    t1 = Thread(target=send_ann_airflow_request, args=[
                                device, job.ID, job.Dag_id, False, config])

                t1.start()

            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class DetectPattern(APIView):
    def post(self, request, device_id):
        data = request.data
        try:
            device = Device.objects.get(ID=device_id)
            aggr_cols = []
            for param in Param.objects.filter(Device=device):
                aggr_cols.append('"{}"'.format(param.Doc_field))

            config = {
                "aggr_cols": ",".join(aggr_cols),
                "n_input": 60,
                "model_file_name": "pattern_detector_v1.h5",

                "start_datetime": (datetime.fromisoformat(data.get('end_datetime')[:-1]) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "end_datetime": data.get('end_datetime'),
            }

            print(config)

            t1 = Thread(target=send_airflow_request, args=[
                        device, device.ID, "detect_pattern_dag", 'pattern', False, config])
            t1.start()

            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class GetAvailableModels(APIView):
    def get(self, request, device_id, format=None):
        device = Device.objects.get(ID=device_id)

        models = MLModel.objects.filter(Job__Device=device)
        payload = {
            'lstm': MLModelSerializer(models.filter(Job__Dag_id='forecast_train_dag'), many=True).data,
            'ann': MLModelSerializer(models.filter(Job__Dag_id='ann_train_dag'), many=True).data
        }
        return Response(payload, status=status.HTTP_200_OK)


@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class JobCompletion(APIView):
    def put(self, request, format=None):
        data = request.data
        # Get data from the headers
        key = request.headers.get('Authorization')
        print(key)
        print(data)
        jobs = AirflowJob.objects.filter(ID=key)
        if jobs.exists():
            job = jobs.first()
            job.Status = data.get('status')
            job.save()

            if job.Type == 'Training' and job.Status == 'Completed':
                col_order = ",".join(data.get('col_order', []))
                MLModel.objects.create(
                    Job=job,
                    N_input=data.get('n_input'),
                    Training_size=data.get('training_size'),
                    File_name=data.get('file_name'),
                    Column_order=col_order
                )

            if job.Type == 'Prediction' and job.Status == 'Completed':
                model = MLModel.objects.get(
                    File_name=data.get('model_file_name'))
                Prediction.objects.create(
                    Model=model,
                    Job=job,
                    File_name=data.get('file_name'),
                    Prediction_size=data.get('prediction_size')
                )

            e_status = job.Status
            file_name = ""
            subject = f"{job.Type} job for [{job.Device.Name}] has been {e_status}"
            email = job.Started_by.email
            send_email([email], subject, e_status, file_name)
            return Response({'message': 'Done'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'Not Done'}, status=status.HTTP_400_BAD_REQUEST)


class GetPredictionView(APIView):
    def get(self, request, prediction_id, format=None):
        prediction = Prediction.objects.get(ID=prediction_id)

        params = [param.Doc_field for param in Param.objects.filter(
            Device=prediction.Job.Device)]

        payload = {
            'meta': PredictionSerializer(prediction).data,
            'predictions': get_predictions(prediction.File_name, params)
        }

        return Response(payload, status=status.HTTP_200_OK)


def send_pattern_detected_data_mail(subject, email_body, sms_body, email_users, sms_users, alert):
    emails = []
    print(email_users)

    for user in email_users:
        to = User.objects.get(username=user)
        emails.append(to.email)

    send_pattern_detected_email_to_user(emails, subject, email_body, alert)

    # for user in sms_users:
    #     to = User.objects.get(username=user)
    #     SendSMS(body=f"{subject} {sms_body}", to=to.profile.Phone)


@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class PatternDetectionCompletedView(APIView):
    def put(self, request, format=None):
        data = request.data
        # Get data from the headers
        key = request.headers.get('Authorization')
        print(key)
        print(data)
        devices = Device.objects.filter(ID=key)
        if devices.exists():
            device = devices.first()

            detectors = PatternDetector.objects.filter(Param__Device=device)
            found_detector_params = []
            found_patterns = []
            for detector in detectors:
                for pattern in detector.Patterns.split(','):
                    if data.get(detector.Param.Doc_field) == pattern:
                        found_detector_params.append(detector.Param.Doc_field)
                        found_patterns.append(pattern)
                        break

            if len(found_detector_params) > 0:
                statement = f"Abnormal patterns detected in " + \
                    ",".join(found_detector_params)+f" for {device.Name}"
                alert = DetectedPatternAlert.objects.create(
                    Name=statement,
                    Device=device,
                    Param_detected_in=",".join(found_detector_params),
                    Detected_pattern=",".join(found_patterns),
                )

                # Email action
                eaction = Action.objects.filter(
                    Misc_id=key, Action='Email', Type='Device')
                email_users = []
                email_body = ""
                if eaction.exists():
                    eaction = eaction.first()
                    email_body = eaction.Body
                    email_users = eaction.User_list.split(
                        ',') if eaction.User_list else []

                # SMS action
                saction = Action.objects.filter(
                    Misc_id=key, Action='SMS', Type='Device')
                sms_users = []
                sms_body = ""
                if saction.exists():
                    saction = saction.first()
                    sms_body = saction.Body
                    sms_users = saction.User_list.split(
                        ',') if saction.User_list else []

                send_pattern_detected_data_mail(
                    statement, email_body, sms_body, email_users, sms_users, alert)
                return Response({'message': 'Done'}, status=status.HTTP_202_ACCEPTED)

            return Response({'message': 'Done'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'Not Done'}, status=status.HTTP_400_BAD_REQUEST)



# Post Device Data using API
def send_request(endpoint, obj=None):
    ELASTIC_HOST = os.getenv("ELASTIC_HOST")
    ELASTIC_KEY = os.getenv("ELASTIC_KEY")

    url = ELASTIC_HOST+f"{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey ' + ELASTIC_KEY
    }
    obj["@timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    payload = json.dumps(obj)
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.json())
    return response


@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class PostData(APIView):
    def post(self, request, device_id, format=None):

        # Create a mutable copy of request.data
        request_data = request.data.copy()
        org_id = request_data.get("org_id")
        api_key = request_data.get("api_key")
        data = request_data.get("data")

        try:
            load_dotenv()
            valid_keys = APIKey.objects.get(Key=api_key)

            response = send_request(
                f"/org-{org_id}-device-{device_id}/_doc", obj=data)

            if response.status_code == 201:
                print('{"Success":"Data added successfully"}', 200)
                return Response('{"Success":"Data added successfully"}', status=status.HTTP_200_OK)
            else:
                print('{"error":"An error occurred"}', 400)
                return Response('{"error":"An error occurred"}', status=status.HTTP_400_BAD_REQUEST)

        except APIKey.DoesNotExist:
            print('{"Error":"Invalid API Key"}', 401)
            return Response('{"Error":"Invalid API Key"}', status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(str(e))
            print('{"Error":"Error"}', 500)
            return Response('{"Error":"Error"}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Talkback(APIView):
    def post(self, request, device_id, action, format=None):
        global client
        global mqtt_data
        dev = Device.objects.get(ID=device_id)
        org_id = dev.UseCase.Division.Organization.ID
        publish(client, org_id, device_id, action, "talkback")

        for i in range(10):
            sleep(0.5)
            if mqtt_data != None:
                print(mqtt_data)
                if "OK" in mqtt_data:
                    temp = mqtt_data
                    mqtt_data = None
                    return Response({'Message': temp}, status=status.HTTP_200_OK)
                else:
                    return Response({'Message': "Status Not OK"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("error")
            return Response({'Message': "No Response from device"}, status=status.HTTP_408_REQUEST_TIMEOUT)

# MQTT Talkback

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(settings.MQTT_CLIENT_ID)
    # Set CA certificate
    client.tls_set(ca_certs='emqxsl-ca.crt')

    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    return client


def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        global mqtt_data
        if msg.topic == "talkback message":
            js = json.loads(msg.payload.decode())
            mqtt_data = js["data"]
            print("I recieved:", mqtt_data)

    client.subscribe(topic)
    client.on_message = on_message


def publish(client, org_id, device_id, data, topic):
    dict = {"org_id": org_id,
            "device_id": device_id,
            "data": data}
    json_data = json.dumps(dict)
    result = client.publish(topic, json_data)
    if result[0] == 0:
        print()
        # print(f"published")
    else:
        print(f"Failed to send message to topic {topic}")


# global mqtt_data
# mqtt_data = None

# global client
# client = connect_mqtt()
# subscribe(client, "talkback message")
# client.loop_start()
