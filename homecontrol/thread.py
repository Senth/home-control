from __future__ import annotations
from typing import Callable
from threading import Thread
from .config import config
from time import sleep

_logger = config.logger


def start_thread(
    function: Callable, seconds_between_calls: float = 1, delay: float = 0
) -> None:
    """Start a function in another thread as a daemon"""
    Thread(target=_run_forever, args=(function, seconds_between_calls, delay))


def _run_forever(
    function: Callable, seconds_between_calls: float, delay: float
) -> None:
    if delay > 0:
        sleep(delay)

    _logger.info(f"Started thread {function.__name__}")
    while True:
        try:
            function()
        except Exception as e:
            _logger.error(f"Error in thread {function.__name__}:\n{e}")

        if seconds_between_calls > 0:
            sleep(seconds_between_calls)