from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



class PostListView(generic.ListView):
    # jobvision_scrap.delay()
    # jobinja_scrap.delay()
    model = Post
    paginate_by = 20
    template_name = 'post_list.html'
    ordering = ['date_modified']
    context_object_name = 'posts'


class FavoriteListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = FavoritePost
    template_name = "favorite.html"
    context_object_name = 'favorites'


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()  # Get the Post instance

        try:
            favorite_post = FavoritePost.objects.get(post=post, user=self.request.user)
        except FavoritePost.DoesNotExist:
            favorite_post = None

        context['favorite_post'] = favorite_post  # Add FavoritePost instance to context
        return context


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


# view.py


class AddToFavoritesView(LoginRequiredMixin,UserPassesTestMixin, View):

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.method == "POST":
            check_favorite = request.POST.get("check_favorite")
            username = request.POST.get("user")
            user = User.objects.get(username=username)

            # Determine whether the checkbox was checked or not
            if check_favorite == "True":
                # Check if the user has already added this post to favorites
                favorite_post, created = FavoritePost.objects.get_or_create(user=user, post=post)
                # Update the is_check field based on the checkbox value
                favorite_post.is_check = True
                favorite_post.save()
                # post.save()
                return redirect('post_detail', pk=post.pk)  # Redirect to a relevant page
            else:
                try:
                    favorite_post = FavoritePost.objects.get(post=post)
                    favorite_post.is_check = False
                    favorite_post.save()
                    favorite_post.delete()
                except FavoritePost.DoesNotExist:
                    pass

                return redirect('post_detail', pk=post.pk)

        return redirect('post_detail', pk=post.pk)   # Redirect if not a POST request



