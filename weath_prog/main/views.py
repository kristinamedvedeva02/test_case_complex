import requests
from django.shortcuts import render, redirect
from django.views import View
from .forms import CityForm
from .models import SearchHistory
from django.http import JsonResponse
from django.db.models import Count


class WeatherView(View):
    form_class = CityForm
    template_name = 'main/index.html'

    def get(self, request):
        form = self.form_class()
        previous_city = request.session.get('previous_city')
        return render(request, self.template_name, {'form': form, 'previous_city': previous_city})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            weather_data = self.get_weather(city)
            request.session['previous_city'] = city

            # # Обновление счетчика запросов
            # search_counts = request.session.get('search_counts', {})
            # if city in search_counts:
            #     search_counts[city] += 1
            # else:
            #     search_counts[city] = 1
            # request.session['search_counts'] = search_counts


            return render(request, 'main/results.html', {'weather_data': weather_data, 'city': city})
        return render(request, self.template_name, {'form': form})

    def get_weather(self, city):
        coordinates = self.get_coordinates(city)
        if not coordinates:
            return None
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coordinates['lat']}&longitude={coordinates['lon']}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_data = [
                {
                    'date': date,
                    'temp_max': temp_max,
                    'temp_min': temp_min,
                }
                for date, temp_max, temp_min in zip(data['daily']['time'], data['daily']['temperature_2m_max'], data['daily']['temperature_2m_min'])
            ]
            return weather_data
        return None

    def get_coordinates(self, city):
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {'lat': data[0]['lat'], 'lon': data[0]['lon']}
        return None

    def save_search_history(self, user, city):
        SearchHistory.objects.create(user=user, city=city)

class CityAutocomplete(View):
    def get(self, request):
        term = request.GET.get('term', '')
        url = f"https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q={term}&limit=10"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cities = [{"id": city["place_id"], "label": city["display_name"], "value": city["display_name"]} for city in data]
            return JsonResponse(cities, safe=False)
        return JsonResponse([], safe=False)


class CitySearchCountAPI(View):
    def get(self, request):
        search_counts = request.session.get('search_history', {})
        search_counts_list = [{'city': city, 'count': count} for city, count in search_counts.items()]
        return JsonResponse(search_counts_list, safe=False)

