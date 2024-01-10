#!/bin/bash

python manage.py migrate

python superuser.py

# python manage.py runserver 0.0.0.0:8000
gunicorn PredCoAPI.wsgi:application --bind 0.0.0.0:8000