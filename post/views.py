from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import jobinja_scrap, jobvision_scrap
from .models import Post
from django.views import generic, View
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from .models import Post, FavoritePost
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.db.models import Count
from django.shortcuts import get_object_or_404

class PostListView(generic.ListView):
    model = Post
    paginate_by = 20
    template_name = 'post_list.html'
    ordering = ['date_modified']
    context_object_name = 'posts'


class FavoriteListView(generic.ListView):
    model = FavoritePost
    template_name = "favorite.html"
    context_object_name = 'favorites'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            return FavoritePost.objects.filter(user_id=user_id)
        else:
            return FavoritePost.objects.none()


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()  # Get the Post instance
        user = self.request.user

        favorite_post = None
        if user.is_authenticated:
            favorite_post = FavoritePost.objects.filter(user=user, post=post).first()

        context['favorite_post'] = favorite_post  # Add FavoritePost instance to context
        return context





def search(request):
    search_result = None
    selected_location = None
    if request.method == "POST":
        search_keyword = request.POST.get("search_keyword")
        location = request.POST.get("location")
        if location == "همه شهر ها":
            location = ""

        q_condition = Q(title__icontains=search_keyword) | \
                      Q(company_name__icontains=search_keyword) | \
                      Q(detail_position__icontains=search_keyword) | \
                      Q(description_position__icontains=search_keyword)

        if location:
            q_condition &= Q(location__icontains=location)

        search_result = Post.objects.filter(q_condition)
        selected_location = location
    return render(request, 'search_result.html', {'search_result': search_result, 'selected_location': selected_location})

# view.py


class AddToFavoritesView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        if request.method == "POST":
            check_favorite = request.POST.get("check_favorite")

            if check_favorite == "True":
                # Add post to favorites
                favorite_post, created = FavoritePost.objects.get_or_create(user=user, post=post)
                favorite_post.is_check = True
                favorite_post.save()
            else:
                # Remove post from favorites
                FavoritePost.objects.filter(user_id=user.id, post=post).delete()

        return redirect('post_detail', pk=post.pk)








