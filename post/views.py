from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from config.celery import app
from time import sleep
from celery import shared_task
from .tasks import jobinja_scrap, jobvision_scrap, update_database
from .models import Post, City
from django.views import generic, View
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from .models import Post, FavoritePost
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.db.models import Count
from django.shortcuts import get_object_or_404


class UrgentPostListView(generic.ListView):
    model = Post
    template_name = 'post_list.html'
    paginate_by = 20
    context_object_name = 'urgent_ads'

    def get_queryset(self):
        # انتخاب دکمه آگهی‌های فوری ذخیره می‌شود
        self.request.session['urgent_selected'] = True
        self.request.session.pop('non_urgent_selected', None)

        return Post.objects.filter(date_modified=-1).order_by('date_modified', 'date_crawled')

class NonUrgentPostListView(generic.ListView):
    model = Post
    template_name = 'post_list.html'
    paginate_by = 20
    context_object_name = 'non_urgent_ads'

    def get_queryset(self):
        self.request.session['non_urgent_selected'] = True
        self.request.session.pop('urgent_selected', None)
        return Post.objects.exclude(date_modified=-1).order_by('date_modified')


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
    # jobinja_scrap.delay()
    # jobvision_scrap.delay()
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

        search_result = Post.objects.filter(q_condition).order_by('date_modified')
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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def search_in_city(request):
    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        # Perform a query to fetch suggested cities based on the search_term
        suggested_cities = City.objects.filter(name__icontains=search_term)[:10]  # Adjust your query as needed

        cities = [city.name for city in suggested_cities]
        return JsonResponse({'cities': cities})

