import boto3
from datetime import datetime, timedelta
import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd
load_dotenv()


def send_airflow_request(device, jobId, dag_id, req_type, train=False, config={}):
    if req_type=="pattern":
        conf_try = '{{"model_file_name": "{}", "index_pattern": "{}", "job_id": "{}", "n_input": {}, "start_datetime": "{}", "end_datetime": "{}", "aggr_cols": [{}]}}'.format(
            config['model_file_name'], device.Index_pattern, jobId, config['n_input'], config['start_datetime'], config['end_datetime'], config['aggr_cols'])

    elif req_type=="twin":
        conf_try = '{{"twin_file_name": "{}", "asset_id": "{}", "twin_id": "{}", "workspace_id": {}, "rules": [{}]}}'.format(
            config['twin_file_name'], config['asset_id'], jobId, config['workspace_id'], config['rules'])

    else:
        if train:
            conf_try = '{{"device_id": "{}", "index_pattern": "{}", "job_id": "{}", "n_input": {}, "filter_date": "{}", "aggr_cols": [{}]}}'.format(
                device.ID, device.Index_pattern, jobId, config['n_input'], config['filter_date'], config['aggr_cols'])
        else:
            conf_try = '{{"device_id": "{}", "index_pattern": "{}", "job_id": "{}", "n_input": {}, "prediction_size": {}, "model_file_name": "{}", "aggr_cols": [{}]}}'.format(
                device.ID, device.Index_pattern, jobId, config['n_input'], config['prediction_size'], config['model_file_name'], config['aggr_cols'])

    raw_data = f"dags trigger {dag_id} -c '{conf_try}'"
    headers = {
        'Authorization': "",
        'Content-Type': 'text/plain'
    }

    response = None
    try:
        client = boto3.client(
            'mwaa',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME')
        )

        token = client.create_cli_token(Name='AirflowTest1')
        headers['Authorization'] = 'Bearer ' + token['CliToken']
        url = f"https://{token['WebServerHostname']}/aws_mwaa/cli"

        response = requests.post(url, data=raw_data, headers=headers)
        return response.json() if response else None
    except:
        return {"Error": "Something snapped!"}

def send_ann_airflow_request(device, jobId, dag_id, train=False, config={}):
    if train:
        conf_try = '{{"device_id": "{}", "index_pattern": "{}", "job_id": "{}", "aggr_cols": [{}], "filter_date": "{}"}}'.format(device.ID, device.Index_pattern, jobId, config['aggr_cols'], config['filter_date'])
    else :
        if config['prediction_type'] == "single":
            conf_try = '{{"device_id": "{}", "job_id": "{}", "prediction_type": "single", "model_file_name": "{}", "col_order": [{}], "recieved_datetime": "{}"}}'.format(device.ID, jobId, config['model_file_name'], config['col_order'], config['recieved_datetime'])
        else:
            conf_try = '{{"device_id": "{}", "job_id": "{}", "prediction_type": "range", "model_file_name": "{}", "col_order": [{}], "start_datetime": "{}", "end_datetime": "{}"}}'.format(device.ID, jobId, config['model_file_name'], config['col_order'], config['start_datetime'], config['end_datetime'])

    raw_data = f"dags trigger {dag_id} -c '{conf_try}'"
    headers = {
        'Authorization' : "",
        'Content-Type': 'text/plain'
    }
    print(conf_try)
    response = None
    try:
        client = boto3.client(
            'mwaa', 
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME')
        )
        
        token = client.create_cli_token(Name='AirflowTest1')
        headers['Authorization'] = 'Bearer ' + token['CliToken']
        url = f"https://{token['WebServerHostname']}/aws_mwaa/cli"
        response = requests.post(url, data=raw_data, headers=headers)

        print(response.json())
        return response.json() if response else None
    except:
        return {"Error": "Something snapped!"}

def send_pattern_detection_airflow_request(device, org, dag_id):
    
    conf_try = '{{"device_name": "{}", "certificateARN": "{}"}}'.format(device.ID, org.CertificateARN)

    raw_data = f"dags trigger {dag_id} -c '{conf_try}'"
    headers = {
        'Authorization': "",
        'Content-Type': 'text/plain'
    }

    response = None
    try:
        client = boto3.client(
            'mwaa',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME')
        )

        token = client.create_cli_token(Name='AirflowTest1')
        headers['Authorization'] = 'Bearer ' + token['CliToken']
        url = f"https://{token['WebServerHostname']}/aws_mwaa/cli"

        response = requests.post(url, data=raw_data, headers=headers)
        return response.json() if response else None
    except:
        return {"Error": "Something snapped!"}

def get_predictions(file_name, params=[]):
    colors = ['red', 'blue', 'green']
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_S3_REGION_NAME')
    )

    # S3 bucket and key for your model
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    model_key = f'Airflow/predictions/{file_name}'  # Adjust the path as needed

    # Download the model file from S3
    print(bucket_name, model_key, file_name)
    s3.download_file(bucket_name, model_key, file_name)

    df = pd.read_csv(file_name)
    cols = df.columns.tolist()
    print(cols)

    predictions = {}
    for param in params:
        color_index = 0
        predictions[param] = []
        for col in cols:
            if param in col:

                data_list = [
                    {
                        'x': timestamp,  # Convert to milliseconds
                        'y': value
                    }
                    for timestamp, value in zip(df['Unnamed: 0'], df[col])
                ]
                print(col, color_index)
                predictions[param].append({
                    'name': col,
                    'data': data_list,
                    'color': colors[color_index]
                })
                color_index += 1

    os.remove(file_name)

    return predictions


def send_iot_airflow_request(device, org, dag_id):
    
    conf_try = '{{"device_name": "{}", "certificateARN": "{}"}}'.format(device.ID, org.CertificateARN)

    raw_data = f"dags trigger {dag_id} -c '{conf_try}'"
    headers = {
        'Authorization': "",
        'Content-Type': 'text/plain'
    }

    response = None
    try:
        client = boto3.client(
            'mwaa',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME')
        )

        token = client.create_cli_token(Name='AirflowTest1')
        headers['Authorization'] = 'Bearer ' + token['CliToken']
        url = f"https://{token['WebServerHostname']}/aws_mwaa/cli"

        response = requests.post(url, data=raw_data, headers=headers)
        return response.json() if response else None
    except:
        return {"Error": "Something snapped!"}
