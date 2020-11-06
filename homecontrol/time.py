from time import time
from datetime import datetime, date
from dateutil import tz


class Time:
    @staticmethod
    def between(start, end):
        now = datetime.now(tz.tzlocal()).time()

        # Same day
        if start <= end:
            return start <= now < end
        else:  # Over midnight
            return start <= now or now < end


class Day:
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @staticmethod
    def is_day(self, *days):
        for day in days:
            if date.today().weekday() == day:
                return True
        return False


class Date:
    @staticmethod
    def between(start, end):
        now = datetime.now(tz.tzlocal())
        now = (now.month, now.day)

        # Same year
        if start <= end:
            return start <= now <= end
        else:  # Across the year
            return start <= now or now <= end
