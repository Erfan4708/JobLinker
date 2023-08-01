@echo off
set DJANGO_SETTINGS_MODULE=config.settings
celery -A config worker -l INFO
