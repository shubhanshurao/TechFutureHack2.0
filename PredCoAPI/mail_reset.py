import requests
from Backend.models import *
from rest_framework.response import Response
from rest_framework import status
import os
from dotenv import load_dotenv
load_dotenv()


def send_email_2_user(to_emails, name, subject, reset_link):
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'application/json',  # Changed content type to JSON
    }

    email_content = f"""
    <html>
    <head></head>
    <body>
        <p>Hello {name},</p>
        <p>Please click on the link below to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
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
                "email": email,
                "name": name
            } for email in to_emails
        ],
        "subject": subject,
        "htmlContent": email_content,
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return Response("Email sent successfully!", status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to send the email. Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
