from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreatSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer


class UserCreateSerializer(BaseUserCreatSerializer):
    class Meta(BaseUserCreatSerializer.Meta):
        fields = ('id', 'username', 'email',
                  'password', 'first_name', 'last_name')


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ('username', 'email', 'first_name', 'last_name')

# class OrganisationSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ('')


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = "__all__"
