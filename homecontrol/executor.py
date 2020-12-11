from __future__ import annotations
from typing import Any, Callable, Dict, List
from .tradfri.effects.effect import Effect
from .config import config
import threading
import time

logger = config.logger


class Executor(threading.Thread):
    _threads: List[Executor] = []

    def __init__(self, target=None, name=None, args=(), kwargs={}) -> None:
        super().__init__(None, target, name, args, kwargs)
        self._terminate = False

    def terminate(self) -> None:
        self._terminate = True

    def execute(self) -> None:
        """Start the action correctly. Don't call run() or start() directly."""
        self.start()
        Executor._threads.append(self)

    @staticmethod
    def terminate_all_running() -> None:
        Executor.clear_all_done()

        logger.debug(
            f"Executor.terminate_running_actions() for {len(Executor._threads)} threads"
        )
        for thread in Executor._threads:
            thread.terminate()
        Executor._threads = []

    @staticmethod
    def clear_all_done() -> None:
        Executor._threads = [
            thread for thread in Executor._threads if thread.is_alive()
        ]


class DelayedExecutor(Executor):
    def __init__(
        self, action: Callable, args: List, kwargs: Dict[str, Any], delay: float
    ) -> None:
        """Run a function after delay seconds

        Args:
            action (Callable): The function to run
            args (List): Positional arguments of the function
            kwargs (Dict): Named arguments of the function
            delay (int): the delay in seconds
        """
        super().__init__(args=[], kwargs={})
        self.args = args
        self.kwargs = kwargs
        self._action = action
        self._delay = delay

    def run(self) -> None:
        """Logic to run in another thread. Never call this directly."""
        logger.debug(
            "DelayedExecutor.run() Delaying execution with "
            + str(self._delay)
            + " seconds."
        )
        time.sleep(self._delay)

        if not self._terminate:
            self._action(*self.args, **self.kwargs)


class EffectExecutor(Executor):
    def __init__(self, effect: Effect) -> None:
        super().__init__()
        self.effect = effect

    def terminate(self) -> None:
        super().terminate()
        self.effect.abort()

    def run(self) -> None:
        """Logic to run in another thread. Never call this directly."""
        self.effect.run()
