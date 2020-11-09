from .weather import Weather
from .luminance import Luminance


class InfoWrapper:
    @staticmethod
    def get_day_info():
        info = {
            "luminance": {"is_dark": int(Luminance.is_dark())},
            "sun": {
                "is_up": int(not Luminance.is_sun_down()),
            },
            "weather": {
                "is_raining": int(Weather.is_raining()),
                "cloud_cover": Weather.get_cloud_coverage(),
            },
        }

        return info
