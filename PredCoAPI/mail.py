import requests
from Backend.models import *
from rest_framework.response import Response
from rest_framework import status
import os
from dotenv import load_dotenv
load_dotenv()

def send_email_to_user(to_emails, subject, body, breached_params):
    # print(to_emails)
    url = 'https://api.brevo.com/v3/smtp/email'
    # print(os.getenv('BREVO_API_KEY'))
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    print(breached_params)
    email_content = """
        <html>
        <head></head>
        <body>
            <p>Alert from PredCo,</p>
            <p>{}</p>
            {}
        </body>
        </html>
    """.format(
        body,
        "\n".join(
            [f"<p>{i.get('param')} ({i.get('value')}) {i.get('condition')} {i.get('threshold')} [threshold]</p>" for i in breached_params]
        ),
    )


    email_data = {
        "sender": {
            "name": "PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def send_anomaly_email_to_user(to_emails, subject, body, alert):
    # print(to_emails)
    url = 'https://api.brevo.com/v3/smtp/email'
    # print(os.getenv('BREVO_API_KEY'))
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    
    email_content = f"""
        <html>
        <head></head>
        <body>
            <h5>Anomaly Alert</h5>
            <i>{body}</i>
            <br/>
            <p>Severity: {alert.Severity}</p>
            <p>Detector: {alert.Detector}</p>
            <p>Time: {alert.Time}</p>
            <p>Typical: {alert.Typical}</p>
            <p>Actual: {alert.Actual}</p>
        </body>
        </html>
    """


    email_data = {
        "sender": {
            "name": "PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def send_missing_data_email_to_user(to_emails, subject, body, alert):
    # print(to_emails)
    url = 'https://api.brevo.com/v3/smtp/email'
    # print(os.getenv('BREVO_API_KEY'))
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    
    email_content = f"""
        <html>
        <head></head>
        <body>
            <h5>Missing data alert !</h5>
            <p>Absence of data is detected for the provided interval.</p>
            <i>{body}</i>
            <br/>
        </body>
        </html>
    """


    email_data = {
        "sender": {
            "name": "PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_email(to_emails, subject, e_status, file_name):
    # print(to_emails)
    url = 'https://api.brevo.com/v3/smtp/email'
    # print(os.getenv('BREVO_API_KEY'))
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    email_content = f"""
        <html>
        <head></head>
        <body>
            <p>Alert from ML@PredCo, </p>
            <p>The Status of the job you have started is <b>{e_status}</b>.</p>
        </body>
        </html>
    """

    email_data = {
        "sender": {
            "name": "ML@PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_geofence_email_to_user(to_emails, subject, body, alert):
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    
    email_content = f"""
        <html>
        <head></head>
        <body>
            <h5>Geofence alert!</h5>
            <p>Movement in asset is captured.</p>
            <i>{body}</i>
            <br/>
        </body>
        </html>
    """


    email_data = {
        "sender": {
            "name": "PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_pattern_detected_email_to_user(to_emails, subject, body, alert):
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'text/plain',
    }
    
    email_content = f"""
        <html>
        <head></head>
        <body>
            <h5>Pattern detection alert!</h5>
            <i>{body}</i>
            <br/>
        </body>
        </html>
    """


    email_data = {
        "sender": {
            "name": "PredCo",
            "email": os.getenv('DEFAULT_FROM_EMAIL')
        },
        "to": [
            {
                "email": email
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
        # "htmlUrl": "https://my.brevo.com/template/F.KGd52nsa1RW7C7AWcEBCwgUu1dblXa2EF.AmGxf6HkgXECh6JP7IA1"
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)