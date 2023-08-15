from django.contrib import admin
from .models import Post, FavoritePost

# Register your models here.
admin.site.register(Post)
admin.site.register(FavoritePost)
