# import os
# from celery import Celery
# from django.conf import settings
# from celery.schedules import crontab
from datetime import timedelta
# from Backend.models import *

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PredCoAPI.settings')

# settings.configure()
# app = Celery('PredCoAPI')
# app.conf.enable_utc = False
# app.conf.update(timezone='Asia/Kolkata')
# app.config_from_object(settings, namespace='CELERY')

# # Automatically discover tasks from installed apps
# app.autodiscover_tasks()

# # Celery Beat configuration
# app.conf.beat_schedule = {
#     'nightly-job': {
#         'task': 'Background_Tasks.tasks.query_elasticsearch',  # Correct import path
#         # 'schedule': crontab(hour=0, minute=0),
#         'schedule': timedelta(seconds=10),
#     },
# }

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')  # Corrected the attribute name 'request'


# import os
# from celery import Celery
# from django.conf import settings
from Backend.models import *

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PredCoAPI.settings')
# app = Celery('PredCoAPI')
# app.conf.enable_utc = False
# app.conf.update(timezone='Asia/Kolkata')
# app.config_from_object(settings, namespace='CELERY')

# # Automatically discover tasks from installed apps
# app.autodiscover_tasks()

# device = Device.objects.all()
# device_ = []
# for i in device:
#     device_id = device.ID
#     device_.append(device_id)
# # Celery Beat configuration

# def generate_schedule(device_id):
#     return {
#         'task': 'Background_Tasks.tasks.query_elasticsearch',
#         'schedule': timedelta(seconds=10),  # Adjust the schedule as needed
#         'args': (device_id,),
#     }

# dynamic_schedules = {f'nightly-job-{device_id}': generate_schedule(device_id) for device_id in device_}

# app.conf.beat_schedule.update(dynamic_schedules)

# app.conf.beat_schedule = {
#     'nightly-job': {
#         'task': 'Background_Tasks.tasks.query_elasticsearch',
#         'schedule': timedelta(seconds=10),
#         'args': device_id
#     },
# }




# celery.py

import os
from celery import Celery
from django.conf import settings
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PredCoAPI.settings')
app = Celery('PredCoAPI')

# Load the Django settings for Celery
app.config_from_object(settings, namespace='CELERY')

# Automatically discover tasks from installed apps
app.autodiscover_tasks()

# Define your dynamic schedule generation function here
def generate_schedule(device_id):
    return {
        'task': 'Background_Tasks.tasks.query_elasticsearch',
        'schedule': timedelta(seconds=10),  # Adjust the schedule as needed
        'args': (device_id,),
    }

# Fetch device IDs dynamically
device_ids = [device.ID for device in Device.objects.all()]

# Create dynamic schedules for each device ID
dynamic_schedules = {f'nightly-job-{device_id}': generate_schedule(device_id) for device_id in device_ids}

# Update Celery Beat schedule with dynamic schedules
app.conf.beat_schedule.update(dynamic_schedules)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

