from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from celery.schedules import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    "jobinja_scrap_task": {
        "task": "post.tasks.jobinja_scrap",
        "schedule": timedelta(minutes=30),
    },
    "jobvision_scrap_task": {
        "task": "post.tasks.jobvision_scrap",
        "schedule": timedelta(minutes=30),
    },
    "update_database_task": {
        "task": "post.tasks.update_database",
        "schedule": crontab(hour=0, minute=0),
    },
}
