import requests
from .config import WEATHER_URL


class Weather:
    """Value in the range of [0,8]"""
    cloud_cover = 0
    temperature = 0
    _weather_info = {}

    @staticmethod
    def _get_weather_info():
        request = requests.get(WEATHER_URL)
        try:
            Weather._weather_info = request.json()
        except ValueError:
            pass

    @staticmethod
    def _set_weather_info():
        parameters = Weather._weather_info['timeSeries'][0]['parameters']

        for parameter in parameters:
            name = parameter['name']
            value = parameter['values'][0]

            if name == 'tcc':
                Weather.cloud_cover = value
            if name == 't':
                Weather.temperature = value

    @staticmethod
    def is_cloudy():
        return Weather.cloud_cover >= 5

    @staticmethod
    def update():
        Weather._get_weather_info()
        Weather._set_weather_info()
