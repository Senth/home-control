from datetime import datetime, timedelta
from ..utils.executor import DelayedExecutor, TimedExecutor
import re
from flask import abort, jsonify
from typing import Any, Callable, Dict, List, Union
from dateutil import tz

_DELAY_STR_REGEX = re.compile(r"^(\d+)_?([a-zA-Z])?$")
_TIME_STR_REGEX = re.compile(r"^(\d{1,2}):(\d{2})$")


def execute(
    body: Dict[str, Any],
    action: Callable,
    args: List = [],
    kwargs: Dict[str, Any] = {},
    delay: float = 0,
    time: Union[datetime, None] = None,
):
    """Execute the action at the correct time; directly, in X seconds, or at XX:XX time.

    Args:
        body (Dict[str, Any]): body from the API call to get delay and time from
        action (Callable): The function to execute
        args (List): arguments
        kwargs (Dict[str, Any]): keyword arguments
    """
    delay = 0
    if "delay" in body:
        delay = get_delay(body["delay"])

    time = None
    if "time" in body:
        time = get_time(body["time"])

    # Delayed
    if delay != 0:
        delayed_executor = DelayedExecutor(
            action=action,
            args=args,
            kwargs=kwargs,
            delay=delay,
        )
        delayed_executor.execute()
    # Execute at time
    elif time:
        timed_executor = TimedExecutor(
            action=action,
            args=args,
            kwargs=kwargs,
            time=time,
        )
        timed_executor.execute()
    # Execute directly
    else:
        action(*args, **kwargs)


def trim_name(names: Union[List[str], str]) -> Union[List[str], str]:
    """Trims the name from the web API, specifically from IFTTT (removes extra "the ")"""

    # Single name
    if isinstance(names, str):
        trimmed_name = names.lower().replace("the", "").strip()
        return trimmed_name
    elif isinstance(names, list):
        trimmed_names: List[str] = []
        for name in names:
            trimmed_names.append(str(trim_name(name)))
        return trimmed_names

    return ""


def get_delay(delay_str: Union[str, int]) -> float:
    """Get the delay from an api call

    Args:
        json (List[str]): The delay from the json body

    Returns:
        int: The delay in seconds, 0 if no delay was found
    """
    delay = 0

    # Already in seconds
    if isinstance(delay_str, int):
        delay = delay_str
    # String delay
    else:
        # Get the value and possible unit
        match = _DELAY_STR_REGEX.match(delay_str)
        if match:
            value, unit = match.groups()
            delay = _get_real_delay(float(value), unit)  # type: ignore
        else:
            abort(
                400,
                f'a time field has an invalid format. Valid format is 3600, "3600", "3600s", "3600 seconds", "60 m", "60 minutes", "1h", "1hour".',
            )

    return delay


def _get_real_delay(delay: float, unit: Union[str, None]) -> float:
    delay_multiplier = 1

    if unit == "m" or unit == "minute" or unit == "minutes":
        delay_multiplier = 60
    elif unit == "h" or unit == "hour" or unit == "hours":
        delay_multiplier = 3600

    return delay * delay_multiplier


def get_time(time_str: str) -> Union[datetime, None]:
    match = _TIME_STR_REGEX.match(time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        # Get in datetime format
        time = datetime.now(tz.tzlocal())
        time = time.replace(hour=hour, minute=minute)

        # Next day if already passed
        if time < datetime.now(tz.tzlocal()):
            time = time + timedelta(days=1)

        return time


def success() -> str:
    return jsonify({"success": True})