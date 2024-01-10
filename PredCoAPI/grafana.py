import boto3
import string
import random
import os
from dotenv import load_dotenv
import json
import time
import subprocess
import requests
import json

load_dotenv()

def create_model(client, model_name):
    # Create a model
    response = client.create_model(
        modelName=model_name,
        modelDescription='Sample model created with Python',
        tags=[]
    )

    model_id = response['modelId']

    return model_id

def create_property(client, model_id, property_name, property_type):
    # Create a property for the model
    response = client.create_property(
        propertyName=property_name,
        propertyType=property_type,
        dataType=property_type,
        unit='None',
        modelId=model_id,
        tags=[]
    )

    property_id = response['propertyId']

    print(f"Model created with ID: {model_id}")
    print(f"Property created with ID: {property_id}")

    return property_id

def create_asset(client, asset_name, model_id):
    # Create an asset
    response = client.create_asset(
        assetName=asset_name,
        assetModelId=model_id,
        tags=[]
    )

    asset_id = response['assetId']
    print(f"Asset created with ID: {asset_id}")

    return asset_id


# client = boto3.client('grafana', region_name='us-west-2')
def Uid(length):
    set = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(set) for _ in range(length))

def token():
    length = 10
    set = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(set) for _ in range(length))

def Idgen():
    length = 15
    base = string.ascii_lowercase + string.ascii_uppercase 
    return ''.join(random.choice(base) for _ in range(length))


def CreateWorkspace(workspaceName):
    client = boto3.client('grafana', region_name='us-west-2')
    configuration = {
        "plugins": {"pluginAdminEnabled": False},
        "unifiedAlerting": {"enabled": False}
    }

    try:
        response = client.create_workspace(
            authenticationProviders=['AWS_SSO'],
            clientToken=token(),  # Call the token function to get the string token
            configuration=configuration,
            grafanaVersion='9.4',
            organizationRoleName=os.getenv('organizationRoleName'),
            permissionType='CUSTOMER_MANAGED',
            workspaceDataSources=[
                'AMAZON_OPENSEARCH_SERVICE', 'CLOUDWATCH', 'PROMETHEUS', 'XRAY', 'TIMESTREAM', 'SITEWISE', 'ATHENA', 'REDSHIFT', 'TWINMAKER'
            ],
            workspaceDescription='This is The Digital Twin Workspace',
            workspaceName=workspaceName,
            workspaceRoleArn=os.getenv('TwinPolicy')
        )
        id = response['workspace']['id']
        url = f"{id}.grafana-workspace.us-west-2.amazonaws.com"
        return {"Url": url,
                "ID_Workspace":id} # Workspace created successfully
    except Exception as e:
        print(f"Error creating workspace: {e}")
        return "Unsuccessful attempt"  # Failed to create workspace



def CreateIdentityCenterUser(username, email, first_name, last_name, mid_name = ''):
    client = boto3.client('identitystore')
    full_name = first_name + mid_name + last_name
    try:
        response = client.create_user(
        IdentityStoreId= os.getenv('IdentityStoreId'),
        UserName= username,
        Name={
            'Formatted': full_name,
            'FamilyName': last_name,
            'GivenName': first_name,
        },
        DisplayName= username,
        ProfileUrl='string',
        Emails=[
            {
                'Value': email,
                # 'Type': 'string', like 'work' 
                'Primary': True
            },
        ],
    )
        return {"Status": "Success",
                "Response": response,
                "ID": response['UserId']}
    except Exception as e:
        print(f"Error creating workspace: {e}")
        return "Unsuccessful attempt" 


def AssignUserAdmin(role, user_id, workspace_id): 
    #role = 'ADMIN'|'EDITOR'|'VIEWER'
    client = boto3.client('grafana', region_name='us-west-2')

    response = client.update_permissions(
    updateInstructionBatch=[
        {
            'action': 'ADD',
            'role': role,
            'users': [
                {
                    'id': user_id,
                    'type': 'SSO_USER'
                },
            ]
        },
    ],
    workspaceId= workspace_id
    )
    return f"Success! The user has been assigned {role} role."


# keyRole
# Specifies the permission level of the key.
# Valid values: VIEWER|EDITOR|ADMIN 

def create_workspace_key(key_name, key_role, seconds_to_live, workspace_id):
    try: 
        # keyRole
        # Specifies the permission level of the key.
        # Valid values: VIEWER|EDITOR|ADMIN 
        client = boto3.client('grafana', region_name='us-west-2')
        response = client.create_workspace_api_key(
        keyName=key_name,
        keyRole= key_role,
        secondsToLive=seconds_to_live,
        workspaceId=workspace_id
        )
        return response['key']
    except Exception as e:
        print(f"The exception is {e}")
        return('Unsuccessful attempt')

def create_folder(Url, Title, Key):
    url = f'https://{Url}/api/folders'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Key}'
    }

    data = {
        "uid": Uid(10),
        "title": Title
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return "Folder successfully created!"
    else:
        return f"Failed to create folder. Status code: {response.status_code}\nError message: {response.text}"

def update_folder(Url, Key, Title, Version, folder_uid):
    url = f'https://{Url}/api/folders/{folder_uid}'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Key}'
    }
    data = {
        "title": Title,
        "version": Version
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return "Folder successfully updated!"
    else:
        return f"Failed to update folder. Status code: {response.status_code}\nError message: {response.text}"   
    
    
def create_dashboard(Url, workspace_id, dashboard_name, panel_name, Key):
        
    url = f'https://{Url}/api/dashboards/db'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Key}'
    }

    payload = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "DashFinal",
            "tags": ["templated"],


    "panels": [
        {
        "datasource": {
            "type": "grafana-iot-twinmaker-datasource",
            "uid": "Tz9rmz4Sz"
        },
        "fieldConfig": {
            "defaults": {
            "color": {
                "mode": "palette-classic"
            },
            "custom": {
                "axisCenteredZero": False,
                "axisColorMode": "text",
                "axisLabel": "",
                "axisPlacement": "auto",
                "barAlignment": 0,
                "drawStyle": "line",
                "fillOpacity": 0,
                "gradientMode": "none",
                "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
                },
                "lineInterpolation": "linear",
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                "type": "linear"
                },
                "showPoints": "auto",
                "spanNulls": False,
                "stacking": {
                "group": "A",
                "mode": "none"
                },
                "thresholdsStyle": {
                "mode": "off"
                }
            },
            "mappings": [],
            "thresholds": {
                "mode": "absolute",
                "steps": [
                {
                    "color": "green",
                    "value": None
                },
                {
                    "color": "red",
                    "value": 80
                }
                ]
            }
            },
            "overrides": []
        },
        "gridPos": {
            "h": 6,
            "w": 12,
            "x": 0,
            "y": 0
        },
        "id": 12,
        "options": {
            "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom",
            "showLegend": True
            },
            "tooltip": {
            "mode": "single",
            "sort": "none"
            }
        },
        "targets": [
            {
            "componentName": "SuspensionMetrics",
            "datasource": {
                "type": "grafana-iot-twinmaker-datasource",
                "uid": "Tz9rmz4Sz"
            },
            "entityId": "30dfb989-958d-4780-8e75-feca6d81035c",
            "filter": [
                {
                "name": "Force",
                "op": "=",
                "value": {}
                }
            ],
            "properties": [
                "Force"
            ],
            "propertyDisplayNames": {},
            "queryType": "EntityHistory",
            "refId": "A"
            }
        ],
        "title": "Suspension Load",
        "type": "timeseries"
        },
        {
        "datasource": {
            "type": "grafana-iot-twinmaker-datasource",
            "uid": "Tz9rmz4Sz"
        },
        "gridPos": {
            "h": 8,
            "w": 12,
            "x": 12,
            "y": 0
        },
        "id": 8,
        "options": {
            "datasource": "",
            "sceneId": "Rail2"
        },
        "targets": [
            {
            "componentName": "SuspensionMetrics",
            "datasource": {
                "type": "grafana-iot-twinmaker-datasource",
                "uid": "Tz9rmz4Sz"
            },
            "entityId": "30dfb989-958d-4780-8e75-feca6d81035c",
            "properties": [
                "Force"
            ],
            "propertyDisplayNames": {},
            "queryType": "EntityHistory",
            "refId": "A"
            }
        ],
        "title": "Bogie",
        "type": "grafana-iot-twinmaker-sceneviewer-panel"
        },
        {
        "datasource": {
            "type": "grafana-iot-twinmaker-datasource",
            "uid": "Tz9rmz4Sz"
        },
        "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 6
        },
        "id": 16,
        "options": {
            "datasource": "",
            "sceneId": "Railway"
        },
        "title": "Train Twin",
        "type": "grafana-iot-twinmaker-sceneviewer-panel"
        },
        {
        "datasource": {
            "type": "grafana-iot-twinmaker-datasource",
            "uid": "Tz9rmz4Sz"
        },
        "fieldConfig": {
            "defaults": {
            "color": {
                "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
                "mode": "absolute",
                "steps": [
                {
                    "color": "green",
                    "value": None
                },
                {
                    "color": "blue",
                    "value": 80
                },
                {
                    "color": "#EAB839",
                    "value": 700
                }
                ]
            }
            },
            "overrides": []
        },
        "gridPos": {
            "h": 6,
            "w": 6,
            "x": 12,
            "y": 8
        },
        "id": 14,
        "options": {
            "orientation": "auto",
            "reduceOptions": {
            "calcs": [
                "lastNotNull"
            ],
            "fields": "",
            "values": False
            },
            "showThresholdLabels": False,
            "showThresholdMarkers": True
        },
        "pluginVersion": "9.4.7",
        "targets": [
            {
            "componentName": "Temperature",
            "datasource": {
                "type": "grafana-iot-twinmaker-datasource",
                "uid": "Tz9rmz4Sz"
            },
            "entityId": "f217fbea-40db-4aa6-816b-776592d039c6",
            "properties": [
                "Temp"
            ],
            "propertyDisplayNames": {},
            "queryType": "EntityHistory",
            "refId": "A"
            }
        ],
        "title": "Engine Temperature",
        "type": "gauge"
        },
        {
        "datasource": {
            "type": "grafana-iot-twinmaker-datasource",
            "uid": "Tz9rmz4Sz"
        },
        "fieldConfig": {
            "defaults": {
            "color": {
                "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
                "mode": "absolute",
                "steps": [
                {
                    "color": "yellow",
                    "value": None
                },
                {
                    "color": "red",
                    "value": 100
                },
                {
                    "color": "#EAB839",
                    "value": 700
                }
                ]
            }
            },
            "overrides": []
        },
        "gridPos": {
            "h": 6,
            "w": 6,
            "x": 18,
            "y": 8
        },
        "id": 18,
        "options": {
            "orientation": "auto",
            "reduceOptions": {
            "calcs": [
                "lastNotNull"
            ],
            "fields": "",
            "values": False
            },
            "showThresholdLabels": False,
            "showThresholdMarkers": True
        },
        "pluginVersion": "9.4.7",
        "targets": [
            {
            "componentName": "SuspensionMetrics",
            "datasource": {
                "type": "grafana-iot-twinmaker-datasource",
                "uid": "Tz9rmz4Sz"
            },
            "entityId": "30dfb989-958d-4780-8e75-feca6d81035c",
            "properties": [
                "Force"
            ],
            "propertyDisplayNames": {},
            "queryType": "EntityHistory",
            "refId": "A"
            }
        ],
        "title": "Force",
        "type": "gauge"
        }
    ],


            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "25s"
        },
        "folderId": 0,
        "folderUid": "EVpefgwmpg",
        "message": "Made changes to xyz",
        "overwrite": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.json())  # If you want to see the response body




def get_folders(Url, Key):
    url = f'https://{Url}/api/folders?limit=10'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Key}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.json())


def get_folders(Url, Key):
    url = f'https://{Url}/api/folders?limit=10'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Key}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.json())



# with open('grafana.json', 'r+') as file:
#     dashboard = json.load(file)


# def update_grid_pos(panel):
#     w = panel['gridPos']['w']
#     h = panel['gridPos']['h']

#     index = 0
#     while True:
#         panel['gridPos']['x'] = (index % w) * w
#         panel['gridPos']['y'] = (index // w) * h

#         yield panel

#         index += 1

# def add_target_and_update_position(panel, target, uid, entity_id, properties, component_name):
#     target["datasource"]["uid"] = uid
#     target["entityId"] = entity_id
#     target["componentName"] = component_name
#     target["properties"] = properties
#     panel['targets'].append(target)
#     return next(update_grid_pos(panel.copy()))

# def update_panel(panel, datasource, scene_id, panel_title):
#     panel["datasource"]["type"] = datasource
#     panel["options"]["sceneId"] = scene_id
#     panel["title"] = panel_title

# # Initial panel configuration
# panel = {
#     "datasource": {
#         "type": "grafana-iot-twinmaker-datasource",
#         "uid": ""  # Replace with the actual uid value
#     },
#     "gridPos": {
#         "h": 8,
#         "w": 12,
#         "x": 0,
#         "y": 0
#     },
#     "options": {
#         "datasource": "",
#         "sceneId":"" # Replace with the actual scene_id value
#     },
#     "targets": [],
#     "title":"",
#     "type": "grafana-iot-twinmaker-sceneviewer-panel"
# }
# target = {
#     "componentName": "",
#     "datasource": {
#         "type": "grafana-iot-twinmaker-datasource",
#         "uid": ""  # Replace with the actual uid value
#     },
#     "entityId": "",  # Replace with the actual entity_id value
#     "properties": [],
#     "propertyDisplayNames": {},
#     "queryType": "EntityHistory",
#     "refId": "A"
# }
# # Function to update gridPos values (unchanged)
# grid_pos_updater = update_grid_pos(panel)

# # Adding targets to panels and updating positions for the first 6 panels (you can continue as needed)
# for _ in range(6):
#     updated_panel = add_target_and_update_position(panel, target.copy(), uid_value, entity_id_value, properties_value, component_name)
#     update_panel(updated_panel, user_datasource, user_scene_id, user_panel_title)
#     updated_grid_pos = next(grid_pos_updater)
#     updated_panel['gridPos'].update(updated_grid_pos['gridPos'])
#     print(f"Panel Title: {updated_panel['title']}, Position: ({updated_panel['gridPos']['x']}, {updated_panel['gridPos']['y']})")


def create_datasource(Name, Key, Url):
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Key}"
    }
    data = {
        "name": Name,
        "type": "grafana-iot-twinmaker-datasource",
        "url": "",
        "access": "proxy",
        "basicAuth": False
    }
    url = f"https://{Url}/api/datasources"
    json_data = json.dumps(data)
    response = requests.post(url, headers=headers, data=json_data)
    if response.status_code == 200:
        print("Datasource created successfully!")
    else:
        print(f"Failed to create datasource. Status code: {response.status_code}")
        print("Response:", response.text)


def enable_permissions(datasource_id, Key, Url):
    # Define the necessary headers and data payload
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Key}"
    }
    data = {}
    url = f"https://{Url}/api/datasources/{datasource_id}/enable-permissions"
    json_data = json.dumps(data)
    response = requests.post(url, headers=headers, data=json_data)
    if response.status_code == 200:
        print(f"Permissions enabled for datasource ID {datasource_id} successfully!")
    else:
        print(f"Failed to enable permissions for datasource ID {datasource_id}. Status code: {response.status_code}")
        print("Response:", response.text)