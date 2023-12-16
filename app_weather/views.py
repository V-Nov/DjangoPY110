from django.shortcuts import render

from utils import current_weather
from django.http import JsonResponse


def weather_view(request):
    if request.method == "GET":
        data = current_weather(60, 30)
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})
