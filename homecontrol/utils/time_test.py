from datetime import datetime, time

import pytest
import time_machine
from dateutil import tz

from .time import Time


@pytest.mark.parametrize(
    "name,start,end,time,expected",
    [
        (
            "At start when exactly right time",
            time(12),
            time(13),
            time(12),
            0.0,
        ),
        (
            "At end when exactly right time",
            time(12),
            time(13),
            time(13),
            1.0,
        ),
        (
            "Halfway when start is before end",
            time(2),
            time(12),
            time(3),
            0.1,
        ),
        (
            "Work from 0 time",
            time(0),
            time(10),
            time(7),
            0.7,
        ),
        (
            "Spanning across midnight",
            time(20),
            time(6),
            time(1),
            0.5,
        ),
    ],
)
def test_percentage_between(name, start, end, time: time, expected):
    print(name)

    date = datetime(2020, 11, 11, time.hour, time.minute, tzinfo=tz.tzlocal())

    with time_machine.travel(date, tick=False):

        actual = Time.percentage_between(start, end)

        assert expected == actual
