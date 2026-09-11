from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post, FavoritePost
from .tasks import save_to_postgres, update_database


def create_post(**kwargs):
    data = {
        'title': 'Python Developer',
        'company_name': 'Example Co',
        'date_modified': 3,
        'location': 'تهران',
        'link': 'https://example.com/jobs/1',
        'website': 'jobinja',
    }
    data.update(kwargs)
    return Post.objects.create(**data)


class PostViewTests(TestCase):
    def test_urgent_and_non_urgent_lists(self):
        create_post(title='Urgent Backend Job', date_modified=-1, link='https://example.com/jobs/2')
        create_post()

        response = self.client.get(reverse('urgent_post_list'))
        self.assertContains(response, 'Urgent Backend Job')
        self.assertNotContains(response, 'Python Developer')

        response = self.client.get(reverse('non_urgent_post_list'))
        self.assertContains(response, 'Python Developer')
        self.assertNotContains(response, 'Urgent Backend Job')

    def test_post_detail(self):
        post = create_post()
        response = self.client.get(reverse('post_detail', args=[post.pk]))
        self.assertContains(response, 'Example Co')

    def test_search_by_keyword_and_location(self):
        create_post()
        create_post(title='UI Designer', location='مشهد', link='https://example.com/jobs/2')

        response = self.client.post(reverse('search'), {'search_keyword': 'python', 'location': ''})
        self.assertContains(response, 'Python Developer')
        self.assertNotContains(response, 'UI Designer')

        response = self.client.post(reverse('search'), {'search_keyword': '', 'location': 'مشهد'})
        self.assertContains(response, 'UI Designer')
        self.assertNotContains(response, 'Python Developer')


class FavoriteTests(TestCase):
    def setUp(self):
        self.post = create_post()
        self.user = User.objects.create_user(username='testuser', password='test-pass-123')
        self.url = reverse('add_to_favorites', args=[self.post.pk])

    def test_add_to_favorites_requires_login(self):
        response = self.client.post(self.url, {'check_favorite': 'True'})
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")
        self.assertFalse(FavoritePost.objects.exists())

    def test_add_and_remove_favorite(self):
        self.client.force_login(self.user)

        self.client.post(self.url, {'check_favorite': 'True'})
        response = self.client.get(reverse('favorite_list'))
        self.assertContains(response, 'Python Developer')

        self.client.post(self.url, {'check_favorite': 'False'})
        self.assertFalse(FavoritePost.objects.filter(user=self.user).exists())


class TaskTests(TestCase):
    def test_save_to_postgres_updates_existing_link(self):
        data = {
            'title': 'Python Developer',
            'company_name': 'Example Co',
            'date_modified': -1,
            'description_position': '',
            'detail_position': '',
            'link': 'https://example.com/jobs/1',
            'location': 'تهران',
            'date_crawled': timezone.now(),
        }
        save_to_postgres(data, 'jobinja')
        save_to_postgres(dict(data, title='Senior Python Developer'), 'jobinja')

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'Senior Python Developer')

    def test_update_database_skips_urgent_posts(self):
        post = create_post(date_modified=0)
        urgent = create_post(date_modified=-1, link='https://example.com/jobs/2')

        update_database()

        post.refresh_from_db()
        urgent.refresh_from_db()
        self.assertEqual(post.date_modified, 1)
        self.assertEqual(urgent.date_modified, -1)
