# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings.split_settings')

# Create a Celery instance and configure it using the settings from Django.
app = Celery('graduation',broker='redis://localhost:6379/0')  # Match the Django project name

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps.
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))