from rest_framework import serializers
from Backend.models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreatSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

class OnboardingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'