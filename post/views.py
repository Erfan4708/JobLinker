from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import my_task_2

# @app.task
# def home_task():
#     print("1111111111111111111111111111111111111111111111111111111111111111111")
#     sleep(10)
#     open("test2.txt", "w").close()


def task(request):
    my_task_2.delay()
    return HttpResponse("Hello")
