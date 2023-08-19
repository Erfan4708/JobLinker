from django.contrib import admin
from .models import Post, FavoritePost, City

# Register your models here.
admin.site.register(Post)
admin.site.register(FavoritePost)
admin.site.register(City)
