from rest_framework import serializers
from Backend.models import *
from Usecases.serializers import *
from Backend.serializers import UserSerializer

class DeviceSerializer(serializers.ModelSerializer):
    UseCase = UsecaseSerializers(read_only=True)
    class Meta:
        model = Device
        fields= '__all__'

class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = "__all__"

class WatcherSerializer(serializers.ModelSerializer):
    # Device = serializers.SlugRelatedField(slug_field='Name', read_only=True)
    Device = DeviceSerializer(read_only=True)
    class Meta:
        model = Watcher
        fields = "__all__"

class AlertSerializer(serializers.ModelSerializer):
    Watcher = WatcherSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = "__all__"


class AirflowJobSerializer(serializers.ModelSerializer):
    Device = DeviceSerializer(read_only=True)
    Started_by = UserSerializer(read_only=True)
    class Meta:
        model = AirflowJob
        fields = "__all__"

class MLModelSerializer(serializers.ModelSerializer):
    Job = AirflowJobSerializer(read_only=True)
    class Meta:
        model = MLModel
        fields = "__all__"

class PredictionSerializer(serializers.ModelSerializer):
    Job = AirflowJobSerializer(read_only=True)
    Model = MLModelSerializer(read_only=True)
    class Meta:
        model = Prediction
        fields = "__all__"

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = "__all__"

class DetectedPatternAlertSerializer(serializers.ModelSerializer):
    Device = DeviceSerializer(read_only=True)
    class Meta:
        model = DetectedPatternAlert
        fields = "__all__"

class PatternDetectorSerializer(serializers.ModelSerializer):
    Param = ParamSerializer(read_only=True)
    class Meta:
        model = PatternDetector
        fields = "__all__"