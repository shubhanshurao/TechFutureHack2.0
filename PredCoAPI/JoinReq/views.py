import requests
from Backend.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from mail import *
import os
from dotenv import load_dotenv
from elastic import *
from Organization.views import *
from datetime import datetime, timedelta
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


load_dotenv()

def send_otp(organizationName, user):
    # Generate the otp
    otp = random.randint(100000, 1000000)
    # Send the password reset message
    subject = 'OTP for email verification.'

    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'api-key': os.getenv('BREVO_API_KEY'),
        'Content-Type': 'application/json',
    }

    email_content = f"""
    <html>
    <head></head>
    <body>
        <h5>You requested a new account creation, with the organization name "{organizationName}"</h5>
        <p>Hello {user.username},</p>
        <p>This is your auto-generated One Time Password (OTP) for email verification.</p>
        <h3>{otp}</h3>
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
                "email": user.email,
            }
        ],
        "subject": subject,
        "htmlContent": email_content,
    }

    try:
        response = requests.post(url, headers=headers, json=email_data)
        print(response.json())
        response.raise_for_status()
        return "OTP sent successfully!", otp
    except requests.exceptions.RequestException as e:
        return f"Failed to send the OTP. Error: {e}", 0

@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class OnboardingForm(APIView):
    def post(self, request, format=None):
        data = request.data

        organization = Organization.objects.create(
            Name=data.get('Name'),
            Phone_Number=data.get('Phone_Number'),
            Website=data.get('Website')
        )

        res = IndextemplateCreation(organization.ID)
        organization.Index_template = res
        organization.CertificateARN=create_CerificateARN(organization)
        organization.save(update_fields=['Index_template','CertificateARN'])

        patterns = [f"org-{organization.ID}-*"]
        # create the role and elastic user
        role_id = ElasticRoleCreation(patterns)
        psswd = ElasticUserCreation(role_id, data.get('username'), data.get('first_name')+data.get('last_name'), data.get('email'), data.get('psswd'))
    
        user = User.objects.create(
            first_name = data.get('first_name'),
            last_name = data.get('last_name'),
            email = data.get('email'),
            username = data.get('username'),
        )
        user.set_password(psswd)
        user.save(update_fields=['password'])

        role = Role.objects.create(
            User=user,
            Organization=organization, 
            Role_name="Account Creator",
            Is_Super_Admin=True,
            password=psswd,
            Role_id=role_id
        )

        profile = Profile.objects.get(Role=role)
        profile.Phone = data.get('user_contact')
        profile.save(update_fields=['Phone'])

        message, otp = send_otp(organization.Name, user)

        if otp>0:
            expired_in = datetime.now() + timedelta(minutes=10)
            VerificationRequest.objects.create(User=user, Otp=str(otp), expired_in=expired_in)

        return Response(message, status=status.HTTP_200_OK)

@authentication_classes([])  # Empty list means no authentication
@permission_classes([AllowAny])  # Allow any user
class VerifyOTP(APIView):
    def post(self, request, username, format=None):
        data = request.data
        user = User.objects.filter(username=username)
        if user.exists():
            user = user.first()
            ver_req = VerificationRequest.objects.filter(User=user, expired_in__lte=datetime.now())
            if ver_req.exists():
                ver_req = ver_req.first()
                if ver_req.Otp == data.get('otp'):
                    role = Role.objects.get(User=user)
                    profile = Profile.objects.get(Role=role)
                    profile.Active = True
                    profile.save(update_fields=['Active'])

                    return Response("Verified succesfully!", status=status.HTTP_200_OK)
                return Response("OTP didn't matched!", status=status.HTTP_200_OK)
            return Response("Request expired or doesn't exist!", status=status.HTTP_200_OK) 
        return Response("User doesn't exist!", status=status.HTTP_200_OK)

class OnboardingStatus(APIView):
    def post(self, request, org_id, api_key,format=None):
        data = request.data
        try: 
            org = Organization.objects.get(ID=org_id)
            status = data.get('Status')
            org.Status = status
            org.save()
            

            # how to get email
            email  = org.Email
            to_emails= [email]
            name = org.Name
            subject='Request Approved '
            send_email_to_user(to_emails, name, subject)
            return Response({'message': 'Status updated successfully'})
        
        except Organization.DoesNotExist:
            return Response({'message': 'Onboarding instance not found'})
        





