from datetime import date, datetime, time
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
