from rest_framework import serializers
from Backend.models import *
from Organization.serializers import DivisionSerializers


class UsecaseSerializers(serializers.ModelSerializer):
    Division = DivisionSerializers(read_only=True)

    class Meta:
        model = UseCases
        fields = '__all__'


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = "__all__"
