from suntime import Sun
from dateutil import tz
import datetime
from .config import LONG, LAT

DIFF_TIME = datetime.timedelta(minutes=30)
sun = Sun(LAT, LONG)


def tomorrow():
    return datetime.datetime.now(tz.tzlocal()) + datetime.timedelta(days=1)


class Sun:
    _sunset = sun.get_local_sunset_time()
    _sunrise = sun.get_local_sunrise_time()
    _last_sunrise = sun.get_local_sunrise_time(datetime.datetime.now(tz.tzlocal()) - datetime.timedelta(days=1))

    @staticmethod
    def update():
        # Always make sure it's the next sunset/sunrise
        now = datetime.datetime.now(tz.tzlocal())

        if now > Sun._sunrise:
            Sun._last_sunrise = Sun._sunrise
            Sun._sunrise = sun.get_local_sunrise_time(tomorrow())

        if now > Sun._sunset:
            Sun._sunset = sun.get_local_sunset_time(tomorrow())

    @staticmethod
    def print():
        print("Sunrise: " + str(Sun._sunrise) + ", sunset: " + str(Sun._sunset))
        print("is_up(): " + str(Sun.is_up()))
        print("is_bright(): " + str(Sun.is_bright()))

    @staticmethod
    def is_up():
        Sun.update()
        return Sun._sunrise > Sun._sunset

    @staticmethod
    def is_down():
        return not Sun.is_up()

    @staticmethod
    def is_bright():
        """Like isUp(), but checks some returns false some time before the sunset and after sunrise"""
        Sun.update()
        sunset = Sun._sunset - DIFF_TIME
        now = datetime.datetime.now(tz.tzlocal())

        # Because we change the time, there are some situations where sunrise > sunset could mean that
        # the sun is still up (or that it's bright outside)
        if Sun._sunrise > Sun._sunset:
            return now < sunset
        else:
            sunrise = Sun._last_sunrise + DIFF_TIME
            return now > sunrise

    @staticmethod
    def is_dark():
        return not Sun.is_bright()
