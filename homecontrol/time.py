from time import time
from datetime import datetime
from dateutil import tz

class Time:
    @staticmethod
    def between(start, end):
        now = datetime.now(tz.tzlocal()).time()

        # Same day
        if start <= end:
            return start <= now < end
        else: # Over midnight
            return start <= now or now < end
