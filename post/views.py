from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import jobinja_scrap

# @app.task
# def home_task():
#     print("1111111111111111111111111111111111111111111111111111111111111111111")
#     sleep(10)
#     open("test2.txt", "w").close()


def task(request):
    jobinja_scrap.delay()
    return HttpResponse("Hello")
