import requests
import json
import os
from Backend.models import *
from elastic_visuals import *
from dotenv import load_dotenv
load_dotenv()

KIBANA_URL = os.getenv('KIBANA_HOST')

def custom_id(length):
    base = string.ascii_uppercase + string.ascii_lowercase + string.digits + ""
    return ''.join(random.choice(base) for _ in range(length))

def send_request(endpoint, obj=None, post_=False, put_=False):
   
    url = f"{os.getenv('ELASTIC_HOST')}{endpoint}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey ' + os.getenv('ELASTIC_KEY')
    }

    response = None
    try:
        if post_:
            payload = json.dumps(obj) if obj else None
            response = requests.request("POST", url, headers=headers, data=payload)
        elif put_:
            payload = json.dumps(obj) if obj else None
            response = requests.request("PUT", url, headers=headers, data=payload)
        else :
            if obj:
                response = requests.get(url, headers=headers, json=obj)
            else:
                response = requests.get(url, headers=headers)
        print(response.json())
        return response if response else None
    except:
        return {"Error": "Something snapped!"}


def CreateDataView(index_pattern_title, pattern):
    url = os.getenv('KIBANA_HOST')
    endpoint = f"/api/data_views/data_view?override=true"

    # Set the authentication token
    headers = {
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
        "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
    }

    # Create the index pattern in Elasticsearch
    data_view = {
        "data_view": {
            "title": pattern,
            "name": index_pattern_title
        }
    }

    response = requests.post(url+endpoint, headers=headers, data=json.dumps(data_view))
    print(response.json())

    return response.json()['data_view']['id']


def IndexPatternCreation(device_id, pattern_type='pm'):
    device = Device.objects.get(ID = device_id)
    org = device.UseCase.Division.Organization
    # Elasticsearch server details
    template_name = org.Index_template # fetched from the org object 

    if pattern_type == 'pm':
        pattern = f"org-{org.ID}-device-{device.ID}-*" 
        pattern_title = f"org_{org.ID}_device_{device.ID}"
    else :
        pattern = f"geo-org-{org.ID}-asset-{device.ID}" 
        pattern_title = f"geo_org_{org.ID}_asset_{device.ID}"

    # Get existing index templat
    endpoint = f'/_index_template/{template_name}'
    response = send_request(endpoint)

    # Check response status
    if response.status_code == 200:
        index_template = response.json()
    else:
        print(f'Failed to retrieve index template. Response: {response.content}')
        exit()

    # Update index template
    index_patterns = index_template['index_templates'][0]['index_template']['index_patterns']

    data_view_id = CreateDataView(pattern_title, pattern)

    index_patterns.append(pattern) 
    # Construct updated index template
    updated_template = {
        "index_patterns": index_patterns,
        # "data_stream": {},
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "location": {
                        "type": "geo_point"
                    }
                }
            }
        }
    }

    # Update index template
    update_endpoint = f'/_index_template/{template_name}'
    update_response = send_request(update_endpoint, obj=updated_template, put_=True)

    if update_response.status_code == 200:
        return pattern, data_view_id
    else:
        return ''



def IndextemplateCreation(org_id, template_type='pm'): #Organiztion

    # Elasticsearch server details
    template_name = ('org_' if template_type=='pm' else 'geo_org_') + org_id.lower()
    default_pattern = f"org-{org_id}-*" if template_type=='pm' else f"geo-org-{org_id}-*"

    # Index template definition
    index_template = {
        "index_patterns": [default_pattern],
        "data_stream": {},
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "location": {
                        "type": "geo_point"
                    }
                }
            }
        }
    }

    # Create index template
    endpoint = f'/_index_template/{template_name}'
    response = send_request(endpoint, obj=index_template, put_=True)
    # Check response status
    if response.status_code == 200: 
       return template_name
    else:
        return ""
    

def ElasticRoleCreation(index_patterns): #Organiztion

    # Elasticsearch server details
    unique_key = custom_id(6)
    role_name = 'role_'+ unique_key

    # Create the role payload
    role_payload = {
        "cluster": ["all"],
        "indices": [
            {
                "names": [ind],
                "privileges": ["all"]
            } for ind in index_patterns
        ],
        "applications": [
            {
                "application": "kibana-.kibana",
                "privileges": ["read"],
                "resources": ["*"]
            }
        ]
    }

    # Create index template
    endpoint = f'/_security/role/{role_name}'
    response = send_request(endpoint, obj=role_payload, put_=True)
    # Check response status
    print(response.json())
    if response.status_code == 200: 
       return role_name
    else:
        return ""


def UpdateRole(index_patterns, role_name):
    endpoint = f'/_security/role/{role_name}'

    response = send_request(endpoint)
    existing_role_definition = response.json()

    # Update the role definition to include the new index patterns
    updated_indices = existing_role_definition.get("indices", [])

    existing_patterns = [pattern.get("names", [])[0] for pattern in updated_indices]

    for index_pattern in index_patterns:
        if index_pattern not in existing_patterns:
            updated_indices.append(
                {
                    "names": [index_pattern],
                    "privileges": ["all"]
                }
            )

    role_payload = {
        "cluster": ["all"],
        "indices": updated_indices,
        "applications": [
            {
                "application": "kibana-.kibana",
                "privileges": ["read"],
                "resources": ["*"]
            }
        ]
    }

    response = send_request(endpoint, obj=role_payload, put_=True)
    # Check response status
    print(response.json())
    if response.status_code == 200: 
       return True
    else:
        return False


def ElasticUserCreation(role, username, full_name, email, psswd = None): #Organiztion

    user_password = psswd if psswd else custom_id(10) 
    # User definition
    user_payload = {
        "password" : user_password,
        "roles" : [ role ],
        "full_name" : full_name,
        "email" : email,
        "metadata" : {
            "intelligence" : 7
        }
    }

    # Create index template
    endpoint = f'/_security/user/{username}'
    response = send_request(endpoint, obj=user_payload, put_=True)
    # Check response status
    if response.status_code == 200: 
       return user_password
    else:
        return ""
        
def decideConfig(param):
    if param.Chart_type in XYcharts:
         return xyChart(param, param.Chart_type)
    elif param.Chart_type == 'pie':
        return pieChart(param)
    else :
        return legacyMetricChart(param)

def CreatePanels(params):
    panels_per_row = 3
    params_ = []

    for i, param in enumerate(params):
        print(i, param.Name)
        config = decideConfig(param)
        params_.append({
            "version": "8.8.2",
            "type": "lens",
            "gridData": {
                "x": (i % panels_per_row) * 16,
                "y": i // panels_per_row * 10,
                "w": 16,
                "h": 10,
                "i": f"param_{param.ID}"
            },
            "panelIndex": f"param_{param.ID}",
            "embeddableConfig": config
        })
    return params_


def DashboardUpdation(params, usecase_id, dashboard_id):
    # Set the Kibana API endpoint URL for creating a dashboard
    # dashboard_id = f"dashboard_{usecase_id}"
    url = os.getenv('KIBANA_HOST')
    endpoint = f"/api/saved_objects/dashboard/{dashboard_id}?overwrite=true"

    # Set the authentication token
    headers = {
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
        "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
    }

    panels = CreatePanels(params)

    dashboard_data = {
        "attributes": {
            "kibanaSavedObjectMeta": {
            "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
            },
            "description": "",
            "timeRestore": False,
            "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"syncCursor\":true,\"syncTooltips\":false,\"hidePanelTitles\":false}",
            "panelsJSON": json.dumps(panels),
            "title": f"{usecase_id} Dashboard",
            "version": 1
        },
    }

    # Send the request to create the dashboard
    response = requests.put(url+endpoint, headers=headers, data=json.dumps(dashboard_data))
    # Retrieve the created dashboard ID
    dashboard_id = response.json()["id"]
    print(dashboard_id)


def DashboardCreation(params, usecase_id):
    # Set the Kibana API endpoint URL for creating a dashboard
   
    url = os.getenv('KIBANA_HOST')
    endpoint = f"/api/saved_objects/dashboard?overwrite=true"

    # Set the authentication token
    headers = {
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
        "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
    }

    panels = CreatePanels(params)

    dashboard_data = {
        "attributes": {
            "kibanaSavedObjectMeta": {
            "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
            },
            "description": "",
            "timeRestore": False,
            "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"syncCursor\":true,\"syncTooltips\":false,\"hidePanelTitles\":false}",
            "panelsJSON": json.dumps(panels),
            "title": f"{usecase_id} Dashboard",
            "version": 1
        },
    }

    # Send the request to create the dashboard
    response = requests.post(url+endpoint, headers=headers, data=json.dumps(dashboard_data))
    print(response.json())
    # Retrieve the created dashboard ID
    dashboard_id = response.json()["id"]

    embedd_url = f"https://predco-elastic.kb.ap-south-1.aws.elastic-cloud.com:9243/app/dashboards#/view/{dashboard_id}?embed=true&_g=(refreshInterval%3A(pause%3A!t%2Cvalue%3A60000)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))&show-time-filter=true"

    return embedd_url, dashboard_id


def JobCreationView(device, params, bucket_span):

    endpoint = f"/_ml/anomaly_detectors/adjob-{device.ID}"
    indice = "_".join(device.Index_pattern.split("-"))
    indice = indice[:len(indice)-3]

    print(indice)

    data = {
        "analysis_config": {
            "bucket_span": bucket_span,
            "detectors": [
                {
                    "function": i['func'], "field_name": f"data.{i['param']}"
                } for i in params
            ]
        },
        "data_description": {
            "time_field": "@timestamp",
            "time_format": "epoch_ms"
        },
        "model_plot_config": {
            "enabled": True
        },
        "results_index_name": f"results-adjob-{device.ID}",
        "datafeed_config": {
            "indices": [
                device.Index_pattern
            ],
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_all": {}
                        }
                    ]
                }
            },
            "datafeed_id": f"datafeed-adjob-{device.ID}"
        }
    }

    response = send_request(endpoint, obj=data, put_=True)
    print(response)

    return f"adjob-{device.ID}"

import datetime

def StartJob(deviceId, job_id):
    endpoint = f"/_ml/anomaly_detectors/{job_id}/_open"
    response = send_request(endpoint, obj={
        "start": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    }, post_=True)

    datafeed_id = f"datafeed-adjob-{deviceId}"
    endpoint = f"/_ml/datafeeds/{datafeed_id}/_start"

    response = send_request(endpoint, obj={
        "start": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    }, post_=True)

    return True


def CreateRule(job, score, interval):
    url = os.getenv('KIBANA_HOST')

    headers = {
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
        "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
    }

    rule_data = {
        "params": {
            "resultType": "bucket",
            "severity": score,
            'jobSelection': {  
                'jobIds': [job.Job_id], 'groupIds': []
            }
        },
        "consumer": "ml",
        "rule_type_id": "xpack.ml.anomaly_detection_alert",
        "schedule": {
            "interval": interval
        },
        "actions": [
            {
                "group": "anomaly_score_match",
                "id": f"28732e80-433c-11ee-ad60-6b482a644bb7", # connector id 
                "params": {
                        "body": {
                            "Authorization": job.Api_key_hash,
                            "Severity": "{{context.score}}",
                            "Time": "{{context.timestamp}}",
                            "Detector": "{{context.field_name}}",
                            "Actual": "{{context.actual}}",
                            "Typical": "{{context.typical}}",
                            "Description": "{{context.message}}"
                        }
                },
            }
        ],
        "tags": [
            "anomaly"
        ],
        "notify_when": "onActionGroupChange",
        "name": f"AD Rule {job.Device.ID}"
    }

    endpoint = f"/api/alerting/rule"
    response = requests.post(url+endpoint, headers=headers, data=json.dumps(rule_data))
    rule_id = response.json()['id']

    return rule_id

def GeofenceWatcherCreation(geofence):
    obj = geofence.Asset if geofence.Asset else geofence.Group_of_Assets

    watcher_name = f"geofence_watcher_{geofence.ID}"
    endpoint = f"/_watcher/watch/{watcher_name}"

    watcher_payload = {
        "trigger": {
            "schedule": {
                "interval": geofence.Frequency
            }
        },
        "actions": {
            "webhook_action": {
                "webhook": {
                    "scheme": "https",   # Adjust the scheme (http/https) as needed
                    "method": "post",
                    "host": "api.predco.ai",
                    "port": 443,   # Replace with the appropriate port number
                    "path": "/Geofencing/check-inside-fence/",
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": f"{geofence.ID}"   # Replace with the actual token
                    },
                    "body": json.dumps({
                        "message": "Hello, this is a scheduled webhook call from Elasticsearch Watcher."
                    })
                }
            }
        }
    }

    print(watcher_payload)
    response = send_request(endpoint, obj=watcher_payload, put_=True)

    response = response.json()
    geofence.Active = True
    geofence.Watcher_id = response.get('_id')
    geofence.save()     


def StartAbnormalPatternDetectorWatcher(device):
    watcher_name = f"pattern_detector_watcher_{device.ID}"
    endpoint = f"/_watcher/watch/{watcher_name}"

    watcher_payload = {
        "trigger": {
            "schedule": {
                "interval": "10m"
            }
        },
        "condition": {
            "always": {}
        },
        "actions": {
            "webhook_1": {
                "webhook": {
                    "scheme": "https",   # Adjust the scheme (http/https) as needed
                    "method": "post",
                    "host": "api.predco.ai",
                    "port": 443,   # Replace with the appropriate port number
                    "path": f"/Devices/ml/detect-pattern/{device.ID}/",
                    "headers": {
                        "Content-Type": "application/json",
                    },
                    "body": json.dumps({
                        "end_datetime": "{{ctx.trigger.triggered_time}}"
                    })
                }
            }
        }
    }

    print(watcher_payload)
    response = send_request(endpoint, obj=watcher_payload, put_=True)

    response = response.json()
