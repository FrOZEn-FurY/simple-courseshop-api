from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseshop_api.settings')

app = Celery('courseshop_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()