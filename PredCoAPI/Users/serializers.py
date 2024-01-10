from rest_framework import serializers
from Backend.models import *
from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreatSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from Organization.serializers import *

class UserCreateSerializer(BaseUserCreatSerializer):
    class Meta(BaseUserCreatSerializer.Meta):
        fields = '__all__'

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'
        # exclude = ('username', 'password')

class RoleSerializer(serializers.ModelSerializer):
    User = UserSerializer(read_only=True)
    Organization = OrganizationSerializers(read_only=True)
    class Meta:
        model = Role
        fields = "__all__"

class ProfileSerializers(serializers.ModelSerializer):
    Role = RoleSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'