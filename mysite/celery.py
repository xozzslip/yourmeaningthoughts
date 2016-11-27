import os
from celery import Celery
from mysite import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

app.config_from_object('mysite.celeryconfig')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
