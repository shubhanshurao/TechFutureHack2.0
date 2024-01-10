from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from Backend.models import *
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from elastic import *
from rest_framework import status

from Usecases.serializers import *
from Devices.serializers import *
from Usecases.models import *
from mail import send_email_to_user, send_anomaly_email_to_user, send_missing_data_email_to_user
from dotenv import load_dotenv
from sms import SendSMS

from Alerts.serializers import *
from Users.serializers import RoleSerializer
from .serializers import *

load_dotenv()
# Create your views here.

def breached(value, threshold, condition):
    if condition == '>':
        return value > threshold
    elif condition == '=':
        return value == threshold

    return value < threshold

def send_alert_mail(subject, email_body, sms_body, email_users, sms_users, breached_params):
    emails = []
    print(email_users)
    
    for user in email_users:
        to = User.objects.get(username=user)
        emails.append(to.email)
    
    send_email_to_user(emails, subject, email_body, breached_params)

    # for user in sms_users:
    #     to = User.objects.get(username=user)
    #     SendSMS(body=f"{subject} {sms_body}", to=to.profile.Phone)

@authentication_classes([])  # Empty list means no authentication classes will be used
@permission_classes([AllowAny])
class ElasticWebhookView(APIView):
    def post(self, request, format=None):
        # Process the data sent by Elastic
        data = json.loads(request.body)
        token = request.headers.get('Authorization')
        
        watcher = Watcher.objects.filter(Api_key_hash=token)
        if watcher.exists():
            print(data)
            
            states = data.get('state', [])
            watcher = watcher.first()

            statement = "Abnormal"
            count = 0
            breached_params = []
            for state in states:    
                if breached(state.get('value'), state.get('threshold'), state.get('condition')):
                    breached_params.append(state)

                    param = Param.objects.get(Device=watcher.Device, Doc_field=state.get('param'))
                    if count > 0:
                        statement += f" and {param.Name}"
                    else : 
                        statement += f" {param.Name}"
                    count += 1
            
            breached_param = [i.get('param') for i in breached_params]
            breached_condition = [i.get('condition') for i in breached_params]
            breached_threshold = [i.get('threshold') for i in breached_params]

            statement += f" in [{watcher.Device.Name}] for [{watcher.Device.UseCase.Name}]"
            alert = Alert.objects.create(
                Name = statement,
                Watcher=watcher,
                Alert_id="Nothing",
                breached_param=",".join(breached_param),
                breached_condition=",".join(breached_condition),
                breached_threshold=",".join(breached_threshold),
            )

            # Email action
            eaction = Action.objects.filter(Watcher=watcher, Action='Email')
            email_users = []
            email_body = ""
            if eaction.exists():
                eaction = eaction.first()
                email_body = eaction.Body
                email_users = eaction.User_list.split(',') if eaction.User_list else []

            # SMS action
            saction = Action.objects.filter(Watcher=watcher, Action='SMS')
            sms_users = []
            sms_body = ""
            if saction.exists():
                saction = saction.first()
                sms_body = saction.Body
                sms_users = saction.User_list.split(',') if saction.User_list else []
            
            send_alert_mail(statement, email_body, sms_body, email_users, sms_users, breached_params)    
            
            return Response({}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_200_OK)



def send_anomaly_mail(subject, email_body, sms_body, email_users, sms_users, alert):
    emails = []
    print(email_users)
    
    for user in email_users:
        to = User.objects.get(username=user)
        emails.append(to.email)
    
    send_anomaly_email_to_user(emails, subject, email_body, alert)

    # for user in sms_users:
    #     to = User.objects.get(username=user)
    #     SendSMS(body=f"{subject} {sms_body}", to=to.profile.Phone)

@authentication_classes([])  # Empty list means no authentication classes will be used
@permission_classes([AllowAny])
class AnomalyWebhookView(APIView):
    def post(self, request, format=None):
        # Process the data sent by Elastic
        data = json.loads(request.body)
        token = request.headers.get('Authorization')
        
        job = Job.objects.filter(Api_key_hash=token)
        if job.exists():
            print(data)
            job = job.first()

            statement = f"Anomaly detected in [{job.Device.Name}] for [{job.Device.UseCase.Name}]"

            alert = AnomalyAlert.objects.create(
                Name = statement,
                Job=job,
                Severity=data.get('Severity'),
                Detector=data.get('Detector'),
                Time=data.get('Time'),
                Typical=data.get('Typical'),
                Actual=data.get('Actual'),
                Description=data.get('Description'),
            )

            # Email action
            eaction = Action.objects.filter(Job=job, Action='Email', Type='Anomaly')
            email_users = []
            email_body = ""
            if eaction.exists():
                eaction = eaction.first()
                email_body = eaction.Body
                email_users = eaction.User_list.split(',') if eaction.User_list else []

            # SMS action
            saction = Action.objects.filter(Job=job, Action='SMS', Type='Anomaly')
            sms_users = []
            sms_body = ""
            if saction.exists():
                saction = saction.first()
                sms_body = saction.Body
                sms_users = saction.User_list.split(',') if saction.User_list else []
            
            send_anomaly_mail(statement, email_body, sms_body, email_users, sms_users, alert)    
            
            return Response({}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_200_OK)


def send_missing_data_mail(subject, email_body, sms_body, email_users, sms_users, alert):
    emails = []
    print(email_users)
    
    for user in email_users:
        to = User.objects.get(username=user)
        emails.append(to.email)
    
    send_missing_data_email_to_user(emails, subject, email_body, alert)

    # for user in sms_users:
    #     to = User.objects.get(username=user)
    #     SendSMS(body=f"{subject} {sms_body}", to=to.profile.Phone)

@authentication_classes([])  # Empty list means no authentication classes will be used
@permission_classes([AllowAny])
class AnomalyMissingDataWebhookView(APIView):
    def post(self, request, format=None):
        # Process the data sent by Elastic
        data = json.loads(request.body)
        token = request.headers.get('Authorization')

        print(token)
        
        watcher = Watcher.objects.filter(Api_key_hash=token)
        if watcher.exists():
            print(data)
            watcher = watcher.first()

            statement = f"Data gap identified at [{data.get('execution_time')}] for [{watcher.Device.Name}]"
            alert = Alert.objects.create(
                Name=statement, 
                Watcher=watcher
            )

            # Email action
            eaction = Action.objects.filter(Watcher=watcher, Action='Email', Type='Watcher')
            email_users = []
            email_body = ""
            if eaction.exists():
                eaction = eaction.first()
                email_body = eaction.Body
                email_users = eaction.User_list.split(',') if eaction.User_list else []

            # SMS action
            saction = Action.objects.filter(Watcher=watcher, Action='SMS', Type='Watcher')
            sms_users = []
            sms_body = ""
            if saction.exists():
                saction = saction.first()
                sms_body = saction.Body
                sms_users = saction.User_list.split(',') if saction.User_list else []
            
            send_missing_data_mail(statement, email_body, sms_body, email_users, sms_users, alert)    
            
            return Response({}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_404_NOT_FOUND)


class GetUsers(APIView):
    def get(self, request, source_type, source_id, format=None):
        roles = []
        if source_type=='watcher':
            source = Watcher.objects.get(ID = source_id)
            roles = Role.objects.filter(Organization=source.Device.UseCase.Division.Organization)
        elif source_type=='usecase': 
            source = UseCases.objects.get(ID=source_id)
            roles = Role.objects.filter(Organization=source.Division.Organization)
            roles = Role.objects.filter(Organization=source.Organization)
        elif source_type=='device':
            source = Device.objects.get(ID=source_id)
            roles = Role.objects.filter(Organization=source.UseCase.Division.Organization)
        else :  
            source = Job.objects.get(ID = source_id)
            roles = Role.objects.filter(Organization=source.Device.UseCase.Division.Organization)

        return Response(RoleSerializer(roles, many=True).data, status=status.HTTP_200_OK)

class WatcherDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            watcher = Watcher.objects.get(pk=pk)
            data = watcher.get_external_data()
            if data is not None:
                return Response(data)
            else:
                return Response({'message': 'Failed to retrieve data from external source'}, status=500)
        except Watcher.DoesNotExist:
            return Response({'message': 'Watcher not found'}, status=404)


    def put(self, request, pk, format=None):
        try:
            watcher = Watcher.objects.get(pk=pk)
            data = request.data
            success = watcher.update_external_data(data)
            if success:
                return Response({'message': 'Watcher data updated successfully'})
            else:
                return Response({'message': 'Failed to update data in external source'}, status=500)
        except Watcher.DoesNotExist:
            return Response({'message': 'Watcher not found'}, status=404)


    def delete(self, request, pk, format=None):
        try:
            watcher = Watcher.objects.get(pk=pk)
            success = watcher.delete_external_data()
            if success:
                watcher.delete()
                return Response({'message': 'Watcher and associated data deleted successfully'})
            else:
                return Response({'message': 'Failed to delete data in external source'}, status=500)
        except Watcher.DoesNotExist:
            return Response({'message': 'Watcher not found'}, status=404)

class AddActionView(APIView):
    def post(self, request, source_type, source_id):
        data = request.data
        if source_type=="watcher":
            source = Watcher.objects.get(ID = source_id)

            Action.objects.create(
                Watcher=source, 
                Action=data.get('Action'), 
                Body=data.get('Body'),
                User_list=",".join(data.get('Users', []))
            )
        elif source_type=="geofence":
            Action.objects.create(
                Misc_id=source_id,
                Type='Geofence',
                Action=data.get('Action'), 
                Body=data.get('Body'),
                User_list=",".join(data.get('Users', []))
            )
        elif source_type=="device":
            Action.objects.create(
                Misc_id=source_id,
                Type='Device',
                Action=data.get('Action'), 
                Body=data.get('Body'),
                User_list=",".join(data.get('Users', []))
            )
        else :
            source = Job.objects.get(ID = source_id)

            Action.objects.create(
                Job=source, 
                Action=data.get('Action'), 
                Body=data.get('Body'),
                User_list=",".join(data.get('Users', [])),
                Type='Anomaly'
            )

        return Response({'message': 'created'}, status=status.HTTP_200_OK)

class CreateWatcherView(APIView):
    def post(self, request, device_id):
        data = request.data

        index_pattern = data.get('index_pattern')
        watcher_name = data.get('watcher_name')
        description = data.get('description')
        interval = data.get('interval')
        Active = True if data.get('Activate')=="true" else False

        conditions = data.get('conditions')
        thresholds = data.get('thresholds')
        params = data.get('params')

        watcher = Watcher.objects.create(
            Name=watcher_name, 
            Description=description,
            Active=Active, 
            Device=Device.objects.get(ID=device_id)
        )

        conditions = conditions.split(',') if conditions else []
        thresholds = thresholds.split(',') if thresholds else []
        params = params.split(',') if params else []

        aggs = {}
        for i in range(len(params)):
            aggs[f'avg_{params[i]}'] = {
                    "avg": {
                        "field": "data."+params[i]
                    }
                }

        condition_script = "return "
        for i in range(len(params)):
            condition_script += f"ctx.payload.aggregations.avg_{params[i]}.value {conditions[i]} {thresholds[i]}"
            if i < len(params) - 1:
                condition_script += " || "
        condition_script += ' ;'

        watcher_name = f"watcher_{watcher.ID}"
        endpoint = f"/_watcher/watch/{watcher_name}"
        
        watcher_payload = {
            "trigger": {
                "schedule": {
                "interval": f"{interval}m"
                }
            },
            "input": {
                "search": {
                "request": {
                    "indices": [index_pattern],
                    "body": {
                    "size": 0,
                    "query": {
                        "bool": {
                        "filter": {
                            "range": {
                            "@timestamp": {
                                "gte": f"now-{interval}m"
                            }
                            }
                        }
                        }
                    },
                    "aggs": aggs
                    }
                }
                }
            },
            "condition": {
                "script": {
                "source": condition_script,
                "lang": "painless"
                }
            },
            "actions": {
                "webhook_to_django": {
                    "webhook": {
                        "scheme": "https",   # Adjust the scheme (http/https) as needed
                        "method": "post",
                        "host": "api.predco.ai",
                        "port": 443,   # Replace with the appropriate port number
                        "path": "/Alerts/webhook/",
                        "headers": {
                            "Content-Type": "application/json",
                            "Authorization": f"{watcher.Api_key_hash}"   # Replace with the actual token
                        },
                        "body": json.dumps({
                            "execution_time": "{{ctx.trigger.triggered_time}}",
                            "state": [
                                {
                                    "param": params[i],
                                    "value": "{{ctx.payload.aggregations.avg_"+params[i]+".value}}",
                                    "threshold": thresholds[i],
                                    "condition": conditions[i]
                                } for i in range(len(params))
                            ]
                        })
                    }
                }
            }
        }
        print(watcher_payload)
        print(watcher.Api_key_hash)
        response = send_request(endpoint, obj=watcher_payload, put_=True)

        response = response.json()
        watcher.Active = True
        watcher.Watcher_id = response.get('_id')
        watcher.save()

        return Response(response, status=status.HTTP_200_OK)



class GetWatchers(APIView):
    def get(self, request, division_id, format=None):
        division = Division.objects.get(ID=division_id)
        uses = UseCases.objects.filter(Division=division)

        uses_ = []
        for use in uses:
            watchers_ = []
            for watcher in Watcher.objects.filter(Device__UseCase=use):
                actions = Action.objects.filter(Watcher=watcher)
                watchers_.append({
                    'details': WatcherSerializer(watcher).data,
                    'actions': [i.Action for i in actions] if actions.exists() else ["No Action"]
                })

            jobs_ = []
            for job in Job.objects.filter(Device__UseCase=use):
                actions = Action.objects.filter(Job=job)
                jobs_.append({
                    'details': JobSerializer(job).data,
                    'actions': [i.Action for i in actions] if actions.exists() else ["No Action"]
                })

            uses_.append({
                'usecase': UsecaseSerializers(use).data,
                'watchers': watchers_,
                'jobs': jobs_
            })

        return Response({'usecases': uses_}, status=status.HTTP_200_OK)

class GetAlerts(APIView):
    def get(self, request, division_id):
        division = Division.objects.get(ID=division_id)

        alerts = Alert.objects.filter(Watcher__Device__UseCase__Division=division)
        anomalies = AnomalyAlert.objects.filter(Job__Device__UseCase__Division=division)    
        detectedpatterns = DetectedPatternAlert.objects.filter(Device__UseCase__Division=division)

        payload = {
            'alerts': AlertSerializer(alerts, many=True).data,
            'anomalies': AnomalyAlertSerializer(anomalies, many=True).data,
            'patterns_detected': DetectedPatternAlertSerializer(detectedpatterns, many=True).data
        }

        return Response(payload, status=status.HTTP_200_OK)  
               
class CreateMissingDataJob(APIView):
    def post(self, request, device_id):
        device = Device.objects.get(ID=device_id)
        data = request.data
        
        watcher = Watcher.objects.create(
            Name=f"Data gap detection watcher for {device.Name}",
            Device=device,
        )

        watcher_name = f"data_gap_watcher_{watcher.ID}"
        endpoint = f"/_watcher/watch/{watcher_name}"
        
        watcher_payload = {
            "trigger": {
                "schedule": {
                "interval": "1m"
                }
            },
            "input": {
                "search": {
                    "request": {
                        "indices": [device.Index_pattern],
                        "body": {
                            "size": 0,
                            "query": {
                                "range": {
                                    "@timestamp": {
                                        "gte": f"now-{data.get('gap_size')}m/m",
                                        "lte": "now/m"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "condition": {
                "compare": {
                    "ctx.payload.hits.total": {
                        "eq": 0
                    }
                }
            },
            "actions": {
                "webhook_to_django": {
                    "webhook": {
                        "scheme": "https",   # Adjust the scheme (http/https) as needed
                        "method": "post",
                        "host": "api.predco.ai",
                        "port": 443,   # Replace with the appropriate port number
                        "path": "/Alerts/data-gap-webhook/",
                        "headers": {
                            "Content-Type": "application/json",
                            "Authorization": f"{watcher.Api_key_hash}"   # Replace with the actual token
                        },
                        "body": json.dumps({
                            "execution_time": "{{ctx.trigger.triggered_time}}",
                        })
                    }
                }
            }
        }
        print(watcher_payload)
        print(watcher.Api_key_hash)
        response = send_request(endpoint, obj=watcher_payload, put_=True)

        response = response.json()
        watcher.Active = True
        watcher.Watcher_id = response.get('_id')
        watcher.save()     

        Action.objects.create(
            Watcher=watcher, 
            Action=data.get('Action'), 
            Body=data.get('Body'),
            User_list=",".join(data.get('Users', []))
        )   

        return Response(response, status=status.HTTP_200_OK)

class CreateJobView(APIView):
    def post(self, request, device_id):
        data = request.data
        device = Device.objects.get(ID=device_id)

        func = data.get('func')
        bucket_span = data.get('bucket_span')

        params = []
        for param in Param.objects.filter(Device=device):
            params.append({
                'func': func, 
                'param': param.Doc_field
            })

        job_id = JobCreationView(device, params, bucket_span)

        job = Job.objects.create(
            Name = f"{device.Name} Anomaly detection job",
            Device=device,
            Job_id=job_id
        )

        # StartJob(device.ID, job_id)

        min_score = data.get('min_score')
        interval = data.get('interval')

        resp = CreateRule(job, min_score, interval)

        return Response({"message": "created"}, status=status.HTTP_200_OK)


class UpdateStatusView(APIView):
    def get(self, request, alert_id, alert_status, format=None):
        alert = Alert.objects.get(ID = alert_id)

        alert.status = alert_status
        alert.save(update_fields=['status'])

        return Response({"message": "done"}, status=status.HTTP_200_OK)

