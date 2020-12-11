import re
from flask import abort, jsonify
from typing import Union
from ..config import config

logger = config.logger
DELAY_STR_REGEX = re.compile(r"^(\d+)_?([a-zA-Z])?$")


def get_time(delay_str: Union[str, int]) -> float:
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
        match = DELAY_STR_REGEX.match(delay_str)
        if match:
            value, unit = match.groups()
            delay = _get_real_time(float(value), unit)  # type: ignore
        else:
            abort(
                400,
                f'a time field has an invalid format. Valid format is 3600, "3600", "3600s", "3600 seconds", "60 m", "60 minutes", "1h", "1hour".',
            )

    return delay


def _get_real_time(delay: float, unit: Union[str, None]) -> float:
    delay_multiplier = 1

    if unit == "m" or unit == "minute" or unit == "minutes":
        delay_multiplier = 60
    elif unit == "h" or unit == "hour" or unit == "hours":
        delay_multiplier = 3600

    return delay * delay_multiplier


def success() -> str:
    return jsonify({"success": True})