import requests
import logging
from .config import WEATHER_URL


logger = logging.getLogger(__name__)


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
                logger.info("Weather.cloud_cover = " + str(value))
            if name == 't':
                Weather.temperature = value
                logger.info("Weather.temperature = " + str(value))

    @staticmethod
    def is_cloudy():
        return Weather.cloud_cover >= 3

    @staticmethod
    def update():
        Weather._get_weather_info()
        Weather._set_weather_info()
