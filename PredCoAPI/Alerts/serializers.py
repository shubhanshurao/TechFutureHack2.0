from rest_framework import serializers
from Backend.models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreatSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

from Devices.serializers import *

class JobSerializer(serializers.ModelSerializer):
    Device = DeviceSerializer(read_only=True)
    class Meta:
        model = Job
        fields = "__all__"

class AnomalyAlertSerializer(serializers.ModelSerializer):
    Job = JobSerializer(read_only=True)
    class Meta:
        model = AnomalyAlert
        fields = "__all__"