from .weather import Weather
from .sun import Sun

import logging

logger = logging.getLogger(__name__)


class InfoWrapper:
    @staticmethod
    def get_day_info():
        info = {
            "sun": {
                "is_up": int(Sun.is_up()),
                "is_bright": int(Sun.is_bright())
            },
            "weather": {
                "is_cloudy": int(Weather.is_cloudy())
            }
        }

        return info
