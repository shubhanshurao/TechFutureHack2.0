from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
import string
import random
from uuid import uuid1
from django.db.models.signals import post_save
from django.dispatch import receiver


def custom_id():
    length = 15
    base = string.ascii_lowercase + string.digits
    return ''.join(random.choice(base) for _ in range(length))


"""
    ID lengths

    Organization 5
    Division 7
    UseCase 7
    Machine 9
    Param 9

"""

# Find a way to Encypt


def keygenerator():
    base = string.ascii_uppercase + string.digits + string.ascii_lowercase + "$=@#&"
    Key = ''.join(random.choice(base) for _ in range(50))
    return Key


# Create your models here.
SERVICES = [
    ('Predictive Maintenance', 'Predictive Maintenance'),
    ('Inventory Management', 'Inventory Management')
]


class Organization(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=100, null=True)
    # Address = models.TextField(null=True)
    # PinCode = models.IntegerField(null=True)
    Contact_person = models.CharField(max_length=150, null=True)
    Phone_Number = models.CharField(max_length=10, null=True)
    Email = models.EmailField(max_length=254, null=True)
    Service = models.CharField(
        choices=SERVICES, max_length=50, default='Predictive Maintenance')
    Status = models.CharField(max_length=150, choices=[
        ('-1', 'Rejected'),
        ('1', 'Approved'),
        ('2', 'Pending')
    ], default=2)
    Website = models.TextField(null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    # elastic field
    Index_template = models.CharField(null=True, max_length=50)

    # AWS IOT
    CertificateARN = models.CharField(null=True, max_length=500)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed Organization'


class Role(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=uuid1, primary_key=True)
    User = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Role_name = models.CharField(max_length=150, null=True)
    Organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)
    Is_Admin = models.BooleanField(default=False, null=True)
    Is_Super_Admin = models.BooleanField(default=False, null=True)
    Mode = models.CharField(max_length=25, choices=[
        ('Viewer', 'Editor'),
        ('Editor', 'Editor'),
        ('Super Editor', 'Super Editor')
    ], default='Viewer')
    password = models.CharField(null=True, max_length=50)
    Division_list = models.CharField(max_length=100, null=True)
    Usecase_list = models.CharField(max_length=200, null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    Role_id = models.CharField(null=True, max_length=100)

    def __str__(self):
        if self.Role_name:
            return self.Role_name

        else:
            return "Unnamed Role"


class Division(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=150, null=True)
    Organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)
    Location = models.CharField(max_length=150, null=True)
    Description = models.TextField(null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed Division'


class UseCases(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=150, null=True)
    Division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True)
    Active = models.BooleanField(default=False)
    Description = models.TextField(null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    # elastic fields
    Dashboard_link = models.URLField(null=True, max_length=300)
    Dashboard_id = models.CharField(null=True, max_length=50)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed UseCase'


class Device(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)  # Primary key
    Unique_Key = models.CharField(
        max_length=50, editable=False, default=keygenerator, unique=True)
    Name = models.CharField(max_length=150, null=True)
    lat = models.CharField(max_length=150, null=True)
    lon = models.CharField(max_length=150, null=True)
    Active = models.BooleanField(default=False, null=True)
    Description = models.TextField(null=True)
    UseCase = models.ForeignKey(UseCases, on_delete=models.CASCADE, null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    # elastic fields
    Index_pattern = models.CharField(null=True, max_length=100)
    Data_view_id = models.CharField(null=True, max_length=100)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed Machine'


DATA_TYPES = [
    ('Integer', 'Integer'),
    ('Boolean', 'Boolean'),
    ('Double', 'Double'),
    ('String', 'String')
]

CHART_TYPES = [
    ('area', 'area'),
    ('line', 'line'),
    ('pie', 'pie'),
    ('metric', 'metric'),
    ('bar_stacked', 'bar_stacked'),
    # ('tagcloud', 'tagcloud'),
    # ('datatable', 'datatable'),
]


class Param(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=150, null=True)
    DataType = models.CharField(
        choices=DATA_TYPES, max_length=50, default='Integer')
    Active = models.BooleanField(default=False)
    Device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)
    Description = models.TextField(null=True)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    # elastic fields
    Visualization_id = models.CharField(null=True, max_length=50)
    Doc_field = models.CharField(max_length=50, null=True)
    Chart_type = models.CharField(
        choices=CHART_TYPES, max_length=50, default='area')

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed Sensor'


class Profile(models.Model):
    Role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    Address = models.TextField(null=True)
    Phone = models.CharField(max_length=10, null=True)
    Active = models.BooleanField(default=False)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)
    Push_Notifications = models.BooleanField(default=True)


@receiver(post_save, sender=Role)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(Role=instance)


class Watcher(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=150, editable=True, null=True)
    Api_key_hash = models.CharField(
        max_length=50, default=keygenerator, null=True, editable=False)
    Description = models.TextField(null=True)
    Device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)
    Watcher_id = models.CharField(max_length=250, null=True)  # elastic id

    Params = models.CharField(max_length=50, null=True)
    Conditions = models.CharField(max_length=50, null=True)
    Thresholds = models.CharField(max_length=50, null=True)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    Active = models.BooleanField(default=False)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return "Unnamed Watcher"


class Alert(models.Model):
    ALERT_CHOICES = [
        ('Closed', 'Closed'),
        ('Canceled', 'Canceled'),
        ('Acknowledged', 'Acknowledged'),
        ('New', 'New'),
    ]

    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=250, editable=True, null=True)
    Watcher = models.ForeignKey(Watcher, on_delete=models.CASCADE, null=True)
    Alert_id = models.CharField(max_length=250, null=True)

    breached_param = models.CharField(max_length=50, null=True)
    breached_condition = models.CharField(max_length=50, null=True)
    breached_threshold = models.CharField(max_length=50, null=True)

    status = models.CharField(choices=ALERT_CHOICES,
                              max_length=50, default='New', null=True)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return "Unnamed Alert"


class Job(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=150, editable=True, null=True)
    Type = models.CharField(max_length=50, choices=[
        ('Anomaly Detection', 'Anomaly Detection')
    ], default='Anomaly Detection')

    Api_key_hash = models.CharField(
        max_length=50, default=keygenerator, null=True, editable=False)
    Device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)
    Job_id = models.CharField(max_length=250, null=True)
    Active = models.BooleanField(default=False)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)


class AnomalyAlert(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(max_length=250, editable=True, null=True)
    Job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)

    Severity = models.CharField(null=True, max_length=50)
    Detector = models.CharField(null=True, max_length=50)
    Time = models.CharField(null=True, max_length=50)
    Typical = models.CharField(null=True, max_length=50)
    Actual = models.CharField(null=True, max_length=50)
    Description = models.CharField(null=True, max_length=50)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)


class Action(models.Model):
    TYPE_CHOICES = [
        ('Watcher', 'Watcher'),
        ('Anomaly', 'Anomaly'),
        ('Geofence', 'Geofence'),
        ('Device', 'Device'),
    ]

    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Action = models.CharField(max_length=50, choices=[
        ('SMS', 'SMS'),
        ('Email', 'Email')
    ])
    Type = models.CharField(choices=TYPE_CHOICES,
                            max_length=50, default='Watcher')
    Body = models.CharField(max_length=1000, null=True)
    User_list = models.CharField(max_length=1000, null=True)

    Watcher = models.ForeignKey(Watcher, on_delete=models.CASCADE, null=True)
    Job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)

    Misc_id = models.CharField(null=True, max_length=50)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.Body:
            return self.Body
        else:
            return "Unnamed Action"

# Machine learning


class AirflowJob(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Device = models.ForeignKey(Device, on_delete=models.CASCADE)

    Name = models.CharField(null=True, max_length=100)
    Start_date = models.DateTimeField(auto_now_add=True, null=True)
    Status = models.CharField(max_length=50, choices=[
        ('In Progress....', 'In Progress....'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ], default="In Progress....")
    Type = models.CharField(max_length=50, choices=[
        ('Training', 'Training'),
        ('Prediction', 'Prediction')
    ], default='Prediction')
    Started_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    Dag_id = models.CharField(null=True, max_length=50)

    def __str__(self):
        return f"{self.Name} {self.Dag_id}"


class MLModel(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Job = models.ForeignKey(AirflowJob, on_delete=models.CASCADE, null=True)

    N_input = models.IntegerField(default=1)
    Training_size = models.IntegerField(default=1)

    File_name = models.CharField(null=True, max_length=200)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)

    Column_order = models.TextField(null=True)

    def __str__(self):
        return self.Job.Name


class Prediction(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Job = models.ForeignKey(AirflowJob, on_delete=models.CASCADE, null=True)
    Model = models.ForeignKey(MLModel, null=True, on_delete=models.CASCADE)

    Prediction_size = models.IntegerField(default=1)

    File_name = models.CharField(null=True, max_length=100)
    Created_date = models.DateTimeField(auto_now_add=True, null=True)


class PatternDetector(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Param = models.ForeignKey(Param, null=True, on_delete=models.CASCADE)
    Patterns = models.CharField(null=True, max_length=500)


class DetectedPatternAlert(models.Model):
    ALERT_CHOICES = [
        ('Closed', 'Closed'),
        ('Canceled', 'Canceled'),
        ('Acknowledged', 'Acknowledged'),
        ('New', 'New'),
    ]

    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)
    Name = models.CharField(null=True, max_length=200)
    Device = models.ForeignKey(Device, null=True, on_delete=models.CASCADE)

    Param_detected_in = models.CharField(null=True, max_length=50)
    Detected_pattern = models.CharField(null=True, max_length=50)

    Status = models.CharField(choices=ALERT_CHOICES,
                              max_length=50, default='New', null=True)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)


class VerificationRequest(models.Model):
    User = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    Otp = models.CharField(null=True, max_length=20)
    expired_in = models.DateTimeField(auto_now=False, auto_now_add=False)


class APIKey(models.Model):
    Role = models.ForeignKey(Role, null=True, on_delete=models.CASCADE)
    Key = models.CharField(null=True, max_length=100)
    last_generated = models.DateTimeField(auto_now_add=True)


class FileUpload(models.Model):
    File = models.FileField(upload_to='uploads/')
    File_name = models.CharField(max_length=255, null=True)
    File_size = models.BigIntegerField(null=True)
    File_format = models.CharField(max_length=50, null=True)
    Timestamp = models.DateTimeField(auto_now_add=True)
    Uploaded_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.file_name if self.file_name else "Unnamed File"
    
class ExtraKey(models.Model):
    ID = models.SlugField(max_length=40, editable=False, default=custom_id, primary_key=True)
    Model_type = models.CharField(max_length=255, null=True)
    Model_id = models.CharField(max_length=255, null=True)
    Key_type = models.CharField(max_length=255, null=True)
    Key_value = models.TextField(null=True)

    def __str__(self) -> str:
        return f"{self.Key_type} for {self.Model_type} [{self.Model_id}]"
