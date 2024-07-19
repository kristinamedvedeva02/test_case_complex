# weather/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', WeatherView.as_view(), name='weather_view'),
    path('autocomplete/', CityAutocomplete.as_view(), name='city_autocomplete'),
    path('api/city-search-count/', CitySearchCountAPI.as_view(), name='city_search_count'),
]
