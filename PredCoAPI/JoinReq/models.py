from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
import string
import random
from uuid import uuid1

# Create your models here.

# class Onboarding(models.Model):
#     ID = models.SlugField(max_length=8, default=uuid1, editable = False, primary_key=True)
#     Name = models.CharField(max_length=150, null = False)
#     Contact_person = models.CharField(max_length=150, null = False)
#     Email = models.EmailField(max_length=150, null=False)
#     Phone = models.IntegerField(max_length=10, null=False)
#     Website = models.CharField(max_length=200, null=False)
#     Status = models.CharField(choices=[
#         ('-1', 'Rejected'),
#         ('1', 'Approved'),
#         ('2', 'Pending')
#     ], default=2)
#     Created_date = models.DateTimeField(auto_now_add=True, null=True)
#     Modified_date = models.DateTimeField(auto_now=True, null=True)

#auto gen pass 
