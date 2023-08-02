from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from celery.schedules import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config", broker=os.environ.get("CELERY_BROKER", "redis://redis:6379/0"))
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "my_task_every_2_seconds": {
        "task": "post.tasks.jobinja_scrap",
        "schedule": timedelta(hours=6),
    },
}
