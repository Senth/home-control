import sys
from subprocess import DEVNULL, CalledProcessError, run
from time import time

from tealprint import TealPrint
from tealprint.tealprint import TealLevel

from ...config import config
from .device import Device


class IpDevice(Device):
    """Checks if a device is on or not."""

    def __init__(
        self,
        ip: str,
        name: str,
        log: bool = False,
        updates_every: int = 15,
        off_times: int = 10,
        timeout: int = 4,
    ):
        super().__init__(f"{name} ({ip})", log)
        self.ip = ip
        self.next_check_in = 0
        self._off_times = off_times
        self._off_times_check = off_times
        self._updates_every = updates_every
        self._timeout = str(timeout)
        self._last_update = 0

    def update(self) -> None:
        # Only update the devices every 15 seconds (we don't want to ping so often)
        elapsed_time = time() - self._last_update
        if elapsed_time >= self._updates_every:
            self._ping_device()
            self._last_update = time()

    def _ping_device(self) -> None:
        last_off_time = self._off_times

        try:
            out = DEVNULL

            if config.general.log_level == TealLevel.debug:
                out = sys.stdout

            run(
                ["ping", "-c", "1", "-W", self._timeout, self.ip],
                check=True,
                stdout=out,
            )
            self._off_times = 0
        except CalledProcessError:
            self._off_times += 1

        if last_off_time >= self._off_times_check and self._off_times == 0:
            self.turned_on()
        if last_off_time == self._off_times_check and self._off_times > self._off_times_check:
            self.turned_off()
        else:
            TealPrint.debug(f"NetworkDevice: {self.ip} {self._off_times}")
