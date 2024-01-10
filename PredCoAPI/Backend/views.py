from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post, PreparedRequest, get
from .models import *
from dotenv import load_dotenv

load_dotenv()

class GetServicesView(APIView):
    def get(self, request, org_id, format=None):
        return Response({'services': ['inventory', 'predective_maintenance']})

# Push Noifications
class SaveDeviceToken(APIView):
    def post(self, request, format=None):
        data = request.data
        user_name = data.get('User_Name') 
        device_token = data.get('Token')  # The device's token

        try:
            devices = ExtraKey.objects.filter(Model_type="user", Model_id=user_name, Key_type="Token")
            if devices.exists():
                devices = devices.first()
                devices_ = set(devices.Key_value.split(","))
                devices_.add(device_token)
                devices.Key_value = ",".join(devices_)
                devices.save()
                return Response({"Success":"Device subscribed successfully"}, status = status.HTTP_200_OK)
            else:
                ExtraKey.objects.create(Model_type="user", Model_id=user_name, Key_type="Token", Key_value=device_token)
                return Response({"Success":"Device subscribed successfully"}, status = status.HTTP_200_OK)
        
        except Exception as e:
            print("Error:", e)
            return Response({"Error":"Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class IndexTemplateCreation(APIView):
#     def post(self, request, format = None):
#         # Elasticsearch server details
#         template_name = 'my_index_template' # "org_" + org.ID

#         # Index template definition
#         index_template = {
#             "index_patterns": [], # list empty for now
#             "settings": {
#                 "number_of_shards": 1,
#                 "number_of_replicas": 0
#             },
#             "mappings": {
#                 "properties": {
#                     "device.location": {
#                         "type": "GeoPoint"
#                     },
#                 }
#             }
#         }

#         # Create index template
#         endpoint = f'/_index_template/{template_name}'
#         response = send_request(endpoint, obj=index_template, put_=True)

#         # Check response status
#         if response.status_code == 200: 
#                 # Save the template_name in the Organization object here
#             print(f'Index template "{template_name}" created successfully.')
#         else:
#             print(f'Failed to create index template. Response: {response.content}')



# class IndexPatternCreation (APIView):
#     def post(self, request, org_id,format = None):



#         # Elasticsearch server details
#         template_name = Organization.Index_template # fetched from the org object 

#         # Get existing index template
#         endpoint = f'/_index_template/{template_name}'
#         response = send_request(endpoint)

#         # Check response status
#         if response.status_code == 200:
#             index_template = response.json()
#         else:
#             print(f'Failed to retrieve index template. Response: {response.content}')
#             exit()

#         # Update index template
#         index_patterns = index_template['index_templates'][0]['index_patterns']
#         pattern = "org-"+Organization.objects.get(ID = org_id)+"-device-"+Devices.ID+"-*"
#         index_patterns.append(pattern) 

#         # Construct updated index template
#         updated_template = {
#             "index_patterns": index_patterns,
#             "settings": {
#                 "number_of_shards": 1,
#                 "number_of_replicas": 0
#             },
#             "mappings": {
#                 "properties": {
#                     "device.location": {
#                         "type": "GeoPoint"
#                     },
#                 }
#             }
#         }

#         # Update index template
#         update_endpoint = f'/_index_template/{template_name}/_update'
#         return Response(send_request(update_endpoint, obj=update_template, put_=True))

#         # Check update response status
#         if update_response.status_code == 200:
#                 # Save the index_pattern in the Device object here
#             print(f'Index template "{template_name}" updated successfully.')
#         else:
#             print(f'Failed to update index template. Response: {update_response.content}')


# class VisualizationCreation(APIView):
#     def post(self, request, format = None):
#         # Set the Elasticsearch endpoint URL for creating a visualization

#         url = "https://my-deployment-fdd076.kb.ap-south-1.aws.elastic-cloud.com:9243/api/saved_objects/visualization/thisVis?overwrite=true"

#         # Set the authentication token
#         headers = {
#             "Content-Type": "application/json",
#             "kbn-xsrf": "true",
#             "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
#         }

#         # Set the visualization JSON payload
#         visualization_data = {
#             "attributes": {
#                 "title": "Temperature Line Chart",
#                 "visState": json.dumps({
#                     "title": "Temperature Line Chart",
#                     "type": "line",
#                     "params": {
#                         "type": "line",
#                         "addTooltip": True,
#                         "addLegend": True,
#                         "legendPosition": "right",
#                         "smoothLines": False,
#                         "xAxisLabel": "@timestamp",
#                         "yAxisLabel": "Temperature",
#                         "yAxisScale": "linear"
#                     },
#                     "aggs": [
#                         {
#                             "id": "1",
#                             "type": "count",
#                             "schema": "metric",
#                             "params": {}
#                         },
#                         {
#                             "id": "2",
#                             "type": "date_histogram",
#                             "schema": "segment",
#                             "params": {
#                                 "field": "@timestamp",
#                                 "interval": "auto",
#                                 "min_doc_count": 1
#                             }
#                         },
#                         {
#                             "id": "3",
#                             "type": "max",
#                             "schema": "metric",
#                             "params": {
#                                 "field": "sensors.temparature"
#                             }
#                         }
#                     ],
#                     "listeners": {}
#                 }),
#                 "uiStateJSON": "{}",
#                 "description": "",
#                 "version": 1,
#                 "kibanaSavedObjectMeta": {
#                     "searchSourceJSON": "{\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\",\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
#                 }
#             },
#             "references": [
#                 {
#                     "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
#                     "type": "metrics-*",
#                     "id": "metrics-*" # this will be fetched from the index_template attribute in the organization 
#                 }
#             ]
#         }

#         # Send the request to create the visualization
#         response = requests.post(url, headers=headers, data=json.dumps(visualization_data))
#         # response = requests.get(url, headers=headers)

#         # Retrieve the visualization ID from the response
#         visualization_id = response.json()
#         print(visualization_id)


# class DashboardCreation(APIView):
#     def post(self, request, format = None):
#         # Set the Kibana API endpoint URL for creating a dashboard
#         url = os.getenv('KIBANA_URL')

#         # Set the authentication token
#         headers = {
#             "Content-Type": "application/json",
#             "kbn-xsrf": "true",
#             "Authorization": "ApiKey " + os.getenv('ELASTIC_KEY')
#         }

#         # Set the dashboard JSON payload
#         dashboard_data = {
#             "attributes": {
#                 "title": "My Dashboard",
#                 "panelsJSON": json.dumps([
#                     {
#                         "panelIndex": 1,
#                         "gridData": {
#                             "x": 0,
#                             "y": 0,
#                             "w": 12,
#                             "h": 6
#                         },
#                         "version": "7.15.0",
#                         "type": "visualization",
#                         "id": visualization_id
#                     }
#                 ]),
#                 "optionsJSON": json.dumps({
#                     "hidePanelTitles": False
#                 })
#             }
#         }

#         # Send the request to create the dashboard
#         response = requests.post(url, headers=headers, data=json.dumps(dashboard_data))

#         # Retrieve the created dashboard ID
#         dashboard_id = response.json()["id"]

#         # Retrieve the shared URL for the dashboard
#         shared_url = f"https://<your-cloud-id>.cloud.elastic.co/app/kibana#/dashboard/{dashboard_id}"

#         print("Dashboard ID:", dashboard_id)
#         print("Shared URL:", shared_url)