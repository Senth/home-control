import requests
from tealprint import TealPrint

from ..config import config
from ..utils.time import Date


class Weather:
    cloud_cover = 0
    """Value in the range of [0,8]"""
    temperature = 0
    _precipitation = 0
    _weather_info = {}

    @staticmethod
    def _get_weather_info():
        request = requests.get(config.location.weather_url())
        try:
            Weather._weather_info = request.json()
        except ValueError:
            TealPrint.warning("⚠ Error fetching weather information")

    @staticmethod
    def _set_weather_info():
        parameters = Weather._weather_info["timeSeries"][0]["parameters"]

        for parameter in parameters:
            name = parameter["name"]
            value = parameter["values"][0]

            if name == "tcc_mean":
                Weather.cloud_cover = value
                TealPrint.info("☁ Weather.cloud_cover = " + str(value))
            if name == "t":
                Weather.temperature = value
                TealPrint.info("♨ Weather.temperature = " + str(value))
            if name == "pmean":
                Weather._precipitation = value
                TealPrint.info("🌧 Weather.precipitation = " + str(value))

    @staticmethod
    def _is_cloudy():
        # Winter
        if Date.between((11, 1), (2, 15)):
            return Weather.cloud_cover >= 3
        # Early Spring / Late Autumn
        elif Date.between((2, 15), (3, 20)) or Date.between((9, 20), (11, 1)):
            return Weather.cloud_cover >= 4
        # Late Spring / Early Autumn
        elif Date.between((3, 20), (4, 1)) or Date.between((9, 1), (9, 20)):
            return Weather.cloud_cover >= 6
        else:
            return False

    @staticmethod
    def get_cloud_coverage():
        """:returns value in the range of [0,8] with 8 being the highest cloud coverage"""
        return Weather.cloud_cover

    @staticmethod
    def is_raining():
        return Weather._precipitation > 0

    @staticmethod
    def update():
        Weather._get_weather_info()
        Weather._set_weather_info()
