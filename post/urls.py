
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('search/', views.search, name='search'),
    path('add-to-favorites/<int:pk>/', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('favorite-list/', views.FavoriteListView.as_view(), name='favorite_list')

]
