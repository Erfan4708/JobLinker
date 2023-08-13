
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('search/', views.search, name='search'),
]
