from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    date_modified = models.IntegerField(blank=True)
    description_position = models.TextField(blank=True)
    detail_position = models.TextField(blank=True)
    link = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    date_crawled = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])


class FavoritePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_check = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])

    def __str__(self):
        return self.post.title