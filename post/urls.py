from django.urls import path, include
from . import views

urlpatterns = [
    path('urgent-posts/', views.UrgentPostListView.as_view(), name='urgent_post_list'),
    path('non-urgent-posts/', views.NonUrgentPostListView.as_view(), name='non_urgent_post_list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('search/', views.search, name='search'),
    path('add-to-favorites/<int:pk>/', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('favorite-list/', views.FavoriteListView.as_view(), name='favorite_list')

]
