from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
import string
import random
from uuid import uuid1
from django.db.models.signals import post_save
from django.dispatch import receiver
from Backend.models import *

def custom_id():
    length = 15
    base = string.ascii_lowercase + string.digits
    return ''.join(random.choice(base) for _ in range(length))
# Create your models here.

TYPE_CHOICES = [
    ('Asset', 'Asset'),
    ('Component', 'Component'),
    ('Simulation', 'Simulation'),
]

class Twin(models.Model):
    ID = models.SlugField(max_length=40, editable=False,
                          default=custom_id, primary_key=True)  # Primary key
    
    Name = models.CharField(max_length=150, null=True)

    Active = models.BooleanField(default=False, null=True)
    Completed = models.BooleanField(default=False, null=True)

    Description = models.TextField(null=True)
    Device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)
    Type = models.CharField(choices=TYPE_CHOICES, max_length=50)

    Created_date = models.DateTimeField(auto_now_add=True, null=True)
    Modified_date = models.DateTimeField(auto_now=True, null=True)

    # elastic fields
    Files = models.TextField(null=True)

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return 'Unnamed Twin'
        

# class IdentityCenter(models.Model):
#     ID = models.CharField(max_length = 20, default = custom_id, editable = False, primary_key = True)
#     Organization = models.ForeignKey(Organization, null = True)


