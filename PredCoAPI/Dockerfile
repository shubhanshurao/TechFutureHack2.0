# FROM python:3.13.0a1-slim-bookworm

# # Set environment variables for Python and unbuffered mode
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# COPY ./requirements.txt /app

# RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY . .

# RUN python manage.py collectstatic --noinput

# # Clean up the build environment
# RUN rm -rf /root/.cache

# # CMD ["bash", "-c", "gunicorn --bind 0.0.0.0:8000 PredCoAPI.wsgi:application"]

# EXPOSE 8000

# CMD [ "python", "manage.py", "runserver" ]



FROM python:3.10-slim-bookworm

# Set environment variables for Python and unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential

# Copy only the requirements file initially
COPY ./requirements.txt /app

# Upgrade pip and install project dependencies
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary

# Copy the entire project to the working directory
COPY . .

RUN python manage.py collectstatic --noinput

# Clean up the build environment
RUN apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

RUN python manage.py migrate

# Expose port 8000
EXPOSE 8000

# Run the application
# When CMD ["python", "manage.py", "runserver"] just this it binds 127.0.0.1 of the container and to access from outside we need to specify 0.0.0.0:8000 this means we can access this from outside/anywhere
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


