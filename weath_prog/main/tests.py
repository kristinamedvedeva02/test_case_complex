from django.test import TestCase
from django.contrib.auth.models import User
from .models import SearchHistory
from .views import WeatherView

class WeatherViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_get_weather(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_post_weather(self):
        response = self.client.post('/', {'city': 'London'})    # Не пройдет, потому что обязательно надо выбрать из выборки городов
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/results.html')

    def test_search_history(self):
        self.client.post('/', {'city': 'London'})
        history = SearchHistory.objects.filter(user=self.user)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().city, 'London')

class CitySearchCountAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        SearchHistory.objects.create(user=self.user, city='London')
        SearchHistory.objects.create(user=self.user, city='Paris')

    def test_city_search_count_api(self):
        response = self.client.get('/api/city-search-count/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['city'], 'London')
        self.assertEqual(data[0]['count'], 1)
        self.assertEqual(data[1]['city'], 'Paris')
        self.assertEqual(data[1]['count'], 1)