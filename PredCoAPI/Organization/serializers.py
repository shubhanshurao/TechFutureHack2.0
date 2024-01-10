from rest_framework import serializers
from Backend.models import *

class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class DivisionSerializers(serializers.ModelSerializer):
    Organization = OrganizationSerializers(read_only=True)
    class Meta:
        model = Division
        fields = '__all__'