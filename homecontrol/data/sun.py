from suntime import Sun
from dateutil import tz
import datetime
from ..config import config

sun = Sun(config.location.lat, config.location.long)

logger = config.logger


def tomorrow():
    return datetime.datetime.now(tz.tzlocal()) + datetime.timedelta(days=1)


class Sun:
    _sunset = sun.get_local_sunset_time()
    _sunrise = sun.get_local_sunrise_time()
    _last_sunrise = sun.get_local_sunrise_time(
        datetime.datetime.now(tz.tzlocal()) - datetime.timedelta(days=1)
    )

    @staticmethod
    def update():
        # Always make sure it's the next sunset/sunrise
        now = datetime.datetime.now(tz.tzlocal())

        if now > Sun._sunrise:
            Sun._last_sunrise = Sun._sunrise
            Sun._sunrise = sun.get_local_sunrise_time(tomorrow())
            logger.info("Sun.update(): Passed sunrise, updating to next day")

        if now > Sun._sunset:
            Sun._sunset = sun.get_local_sunset_time(tomorrow())
            logger.info("Sun.update(): Passed sunset, updating to next day")

    @staticmethod
    def print():
        print(f"Sunrise: {Sun._sunrise} , sunset: {Sun._sunset}")
        print(f"is_up(): {Sun.is_up()}")
        print(f"is_bright(): {Sun.is_up_shortened()}")

    @staticmethod
    def is_up():
        Sun.update()
        return Sun._sunrise > Sun._sunset

    @staticmethod
    def is_down():
        return not Sun.is_up()

    @staticmethod
    def is_up_shortened(hours=0, minutes=30):
        """Like isUp(), but checks some returns false some time before the sunset and after sunrise"""
        Sun.update()

        diff_time = datetime.timedelta(hours=hours, minutes=minutes)

        # Because we change the time, there are some situations where sunrise > sunset could mean that
        # the sun is still up (or that it's bright outside)
        if Sun._sunset > Sun._sunrise:
            return False
        else:  # Sun is up (but it might not be bright yet/still)

            now = datetime.datetime.now(tz.tzlocal())
            sunset = Sun._sunset - diff_time
            # until 30 min before sunset -> it's not bright
            if now > sunset:
                return False

            # until 30 min after sunrise -> it's not bright
            sunrise = Sun._last_sunrise + diff_time
            if now < sunrise:
                return False

            return True

    @staticmethod
    def is_down_shortened(hours=0, minutes=30):
        return not Sun.is_up_shortened(hours=hours, minutes=minutes)
