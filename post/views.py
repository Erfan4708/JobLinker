from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import jobinja_scrap, jobvision_scrap
from .models import Post
from django.views import generic
from django.db.models import Q



class PostListView(generic.ListView):
    # jobvision_scrap.delay()
    # jobinja_scrap.delay()
    model = Post
    paginate_by = 20
    template_name = 'post_list.html'
    ordering = ['date_modified']
    context_object_name = 'posts'


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'


def search(request):
    search_result = None
    if request.method == "POST":
        search_keyword = request.POST.get("search_keyword")
        q_condition = Q(title__icontains=search_keyword) | \
                      Q(company_name__icontains=search_keyword) | \
                      Q(detail_position__icontains=search_keyword) | \
                      Q(description_position__icontains=search_keyword) | \
                      Q(location__icontains=search_keyword)

        search_result = Post.objects.filter(q_condition)
    return render(request, 'search_result.html', {'search_result': search_result})
