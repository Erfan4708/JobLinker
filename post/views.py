from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import jobinja_scrap, jobvision_scrap
from .models import Post
from django.views import generic


class PostListView(generic.ListView):
    # jobvision_scrap.delay()
    # jobinja_scrap.delay()
    model = Post
    paginate_by = 20
    template_name = 'post_list.html'
    context_object_name = 'posts'


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'
