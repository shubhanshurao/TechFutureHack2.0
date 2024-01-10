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
from Usecases.serializers import *
from Backend.serializers import *
import random
import datetime

# Create your views here.


def keygenerator(length):
    base = string.ascii_uppercase + string.digits + string.ascii_lowercase
    Key = ''.join(random.choice(base) for _ in range(length))
    return Key


class CreateUser(APIView):
    # how to map user to an organization map in profile
    def post(self, request, org_id, format=None):
        try:
            data = request.data
            usecases = data.get('usecases').split(
                ',') if data.get('usecases') else []
            org = Organization.objects.get(ID=org_id)

            patterns = []
            for use in usecases:
                usec = UseCases.objects.get(ID=use)
                for device in Device.objects.filter(UseCase=usec):
                    patterns.append(device.Index_pattern)

            # create the role
            role_id = ""
            if len(patterns) > 0:
                role_id = ElasticRoleCreation(patterns)
                # create the elastic user
                psswd = ElasticUserCreation(role_id, data.get('username'), data.get(
                    'first_name')+data.get('last_name'), data.get('email'))
            else:
                psswd = keygenerator(10)

            user = User.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                username=data.get('username'),
            )
            user.set_password(psswd)

            user.save(update_fields=['password'])

            role = Role.objects.create(
                User=user,
                Organization=org,
                Role_name=data.get('role_name'),
                Is_Admin=data.get('role') == 'admin',
                Is_Super_Admin=data.get('role') == 'super-admin',
                Mode=data.get('mode'),
                Division_list=data.get('divisions'),
                Usecase_list=data.get('usecases'),
                password=psswd,
                Role_id=role_id
            )

            return Response({'message': 'User created successfully', 'password': psswd}, status=status.HTTP_202_ACCEPTED)
        except Organization.DoesNotExist:
            return Response({'message': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': "Unable to Create the User"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfile(APIView):
    def put(self, request, user_id, format=None):
        data = request.data
        try:
            profile = Profile.objects.get(id=user_id)  # ask
            role = data.get('Role')
            if role in ['Super Admin', 'Admin', 'User']:
                profile.Role = role
                profile.save()
                return Response({'message': 'Role updated successfully'}, status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class ViewUsers(APIView):
    def get(self, request, org_id, format=None):
        try:
            org = Organization.objects.get(ID=org_id)
            roles = Role.objects.filter(Organization=org)

            payload = {
                'users': RoleSerializer(roles, many=True).data,
                'usecases': UsecaseSerializers(UseCases.objects.filter(Division__Organization=org), many=True).data,
            }

            return Response(payload, status=status.HTTP_200_OK)

        except Organization.DoesNotExist:
            return Response({'message': 'Unable to find Users'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'Unable to View User'}, status=status.HTTP_400_BAD_REQUEST)


class ViewUser(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user).data

            return Response(serializer)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)


class DeleteUser(APIView):
    def post(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'Data deleted successfully'}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class GetMyOrganization(APIView):
    def get(self, request, username, format=None):
        try:
            user = User.objects.get(username=username)
            role = Role.objects.get(User=user)
            payload = {
                'org': OrganizationSerializers(role.Organization).data,
                'role': RoleSerializer(role).data
            }
            return Response(payload, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'message': 'Unable to delete Data'}, status=status.HTTP_202_ACCEPTED)


class GetProfileDetails(APIView):
    def get(self, request, username, format=None):
        user = User.objects.get(username=username)
        profile = Profile.objects.get(Role__User=user)
        divs = Division.objects.filter(Organization=profile.Role.Organization)

        payload = {
            'divisons': DivisionSerializers(divs, many=True).data,
            'profile': ProfileSerializers(profile).data
        }

        return Response(payload, status=status.HTTP_200_OK)

    def put(self, request, username, format=None):
        data = request.data

        user = User.objects.get(username=username)
        user.email = data.get('email')
        user.first_name = data.get('firstName')
        user.last_name = data.get('lastName')
        user.save()

        profile = Profile.objects.get(Role__User=user)
        profile.Phone = data.get('phone')
        profile.save()

        return Response({'message': 'Done'}, status=status.HTTP_200_OK)


class GetAPIKeyView(APIView):
    def get(self, request, username, format=None):
        role = Role.objects.get(User__username=username)

        key = APIKey.objects.get(Role=role)
        payload = APIKeySerializer(key).data

        return Response(payload, status=status.HTTP_200_OK)


def api_key_generator():
    length = 50
    base = string.ascii_lowercase + string.digits + string.ascii_uppercase + "@#$"
    return ''.join(random.choice(base) for _ in range(length))


class GenerateAPIKey(APIView):
    def get(self, request, username, format=None):
        # role = Role.objects.filter(User__username=username)
        role = Role.objects.get(User__username=username)

        key = APIKey.objects.filter(Role=role)
        if key.exists():
            key = key.first()
            key.Key = api_key_generator()
            key.last_generated = datetime.datetime.now()
            key.save(update_fields=['Key'])
        else:
            key = APIKey.objects.create(Role=role, Key=api_key_generator())

        return Response({'key': key.Key}, status=status.HTTP_200_OK)
    

class EnableUserNotification(APIView):
    def get(self, request, username, format=None):
        data=request.data
        user=User.objects.get(username=username)
        role = Role.objects.get(User=user)
        profile=Profile.objects.get(Role=role)
        return Response(profile.Push_Notifications, status=status.HTTP_200_OK)
    
    def put(self, request, username, format=None):
        data=request.data
        user=User.objects.get(username=username)
        role = Role.objects.get(User = user)
        profile = Profile.objects.get(Role = role)
        profile.Push_Notifications = data
        profile.save()
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)



