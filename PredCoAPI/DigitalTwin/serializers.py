from rest_framework import serializers
from .models import *
from Devices.serializers import *

class TwinSerializer(serializers.ModelSerializer):
    Device = DeviceSerializer(read_only=True)
    class Meta:
        model = Twin
        fields= '__all__'