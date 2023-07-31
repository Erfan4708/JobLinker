from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # اصلاح اشتباه املایی در این خط
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")  # اصلاح اشتباه املایی در این خط
app.autodiscover_tasks()
