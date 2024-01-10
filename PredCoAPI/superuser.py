# create_superuser.py
import os
import django

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PredCoAPI.settings")
django.setup()

from django.contrib.auth import get_user_model

# Fetching variables from environment
username = os.getenv("DJANGO_USER")
email = os.getenv("DJANGO_EMAIL")
password = os.getenv("DJANGO_PASS")

# Creating superuser
User = get_user_model()
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created successfully!")

elif User.objects.filter(username=username).exists():
    print("User exists")
    
else:
    print("Issue")
