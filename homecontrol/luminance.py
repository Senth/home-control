from .weather import Weather
from .sun import Sun
from .time import Date
from .config import config

logger = config.logger

SUMMER_START = (4, 1)
AUTUMN_EARLY_START = (9, 1)
AUTUMN_LATE_START = (9, 20)
WINTER_START = (11, 1)
SPRING_EARLY_START = (2, 15)
SPRING_LATE_START = (3, 20)


class Luminance:
    @staticmethod
    def is_dark() -> bool:
        # Return directly if sun is actually down
        if Luminance.is_sun_down():
            return True

        # Else the sun is up and we check whether the weather is dark
        if Luminance._is_weather_dark():
            # If it's summer, only check an hour after sunrise before sunset
            if Date.between(SUMMER_START, AUTUMN_EARLY_START):
                if Sun.is_down_shortened(hours=1, minutes=0):
                    return True
            # Not summer, therefore it's always dark
            else:
                return True

        return False

    @staticmethod
    def is_sun_down() -> bool:
        """Get sun is down depending on which date it is"""
        if Date.between(SPRING_LATE_START, AUTUMN_LATE_START):
            return Sun.is_down()
        else:
            return Sun.is_down_shortened()

    @staticmethod
    def _is_weather_dark() -> bool:
        """:returns true if it's cloudy, checks how cloudy it is depending on the year"""
        # Winter
        if Date.between(WINTER_START, SPRING_EARLY_START):
            return Weather.cloud_cover >= 3
        # Early Spring / Late Autumn
        elif Date.between(SPRING_EARLY_START, SPRING_LATE_START) or Date.between(
            AUTUMN_LATE_START, WINTER_START
        ):
            return Weather.cloud_cover >= 4
        # Late Spring / Early Autumn
        elif Date.between(SPRING_LATE_START, SUMMER_START) or Date.between(
            AUTUMN_EARLY_START, AUTUMN_LATE_START
        ):
            return Weather.cloud_cover >= 6
        # Summer
        else:
            return Weather.cloud_cover == 8
