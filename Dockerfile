# syntax=docker/dockerfile:1
FROM python:3.11
COPY . .
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
EXPOSE 8080
CMD ["python", "main_appengine.py"]

# These steps upload your Application Default Credentials as temporary secret files.
# (ADC usually provided through "gcloud auth appliation-default login" command)
RUN --mount=type=secret,id=gcloud_adc,dst=/tmp/application_default_credentials.json \
mkdir -p /home/.config/gcloud/ && \
cp /tmp/application_default_credentials.json /home/.config/gcloud/application_default_credentials.json

# This line defines the path for your uploaded credentials and sets it to ADC environment variable used to auhtenticate
# (for more info check https://cloud.google.com/docs/authentication/application-default-credentials#personal)
ENV GOOGLE_APPLICATION_CREDENTIALS=/home/.config/gcloud/application_default_credentials.json

# Set the project ID environment variable used to identify the using project:
ENV GOOGLE_CLOUD_PROJECT="starting-with-python-473014"