from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Tuple

from dateutil import tz


class Time:
    @staticmethod
    def between(start: time, end: time) -> bool:
        now = datetime.now(tz.tzlocal()).time()

        # Same day
        if start <= end:
            return start <= now < end
        else:  # Over midnight
            return start <= now or now < end

    @staticmethod
    def percentage_between(start: time, end: time) -> float:
        now = datetime.now(tz.tzlocal())
        datetime_start = datetime(now.year, now.month, now.day, start.hour, start.minute)
        datetime_end = datetime(now.year, now.month, now.day, end.hour, end.minute)

        # Over midnight
        if start >= end:
            datetime_end = datetime_end + timedelta(days=1)

        datetime_diff = datetime_end - datetime_start
        total_diff_sec = datetime_diff.total_seconds()

        datetime_diff = now - datetime_start
        diff_sec = datetime_diff.total_seconds()

        return diff_sec / total_diff_sec


class Days(Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Day:
    @staticmethod
    def is_day(*days: Days) -> bool:
        for day in days:
            if date.today().weekday() == day.value:
                return True
        return False

    @staticmethod
    def is_weekend() -> bool:
        return Day.is_day(Days.saturday, Days.sunday)

    @staticmethod
    def is_workday() -> bool:
        return not Day.is_weekend()


class Date:
    @staticmethod
    def between(start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        now = datetime.now(tz.tzlocal())
        now = (now.month, now.day)

        # Same year
        if start <= end:
            return start <= now <= end
        else:  # Across the year
            return start <= now or now <= end
