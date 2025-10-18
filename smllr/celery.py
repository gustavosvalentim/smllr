import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smllr.settings")


app = Celery("smllr")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

