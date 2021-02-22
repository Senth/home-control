from .device import Device
from .unifi_api import UnifiApi
from time import time


api = UnifiApi()


class UnifiDevice(Device):
    def __init__(
        self,
        name: str,
        mac_address: str,
        log: bool = False,
        max_off_time: int = 300,
    ) -> None:
        super().__init__(name, log)
        self._mac_address = mac_address
        self._max_off_time = max_off_time

    def update(self) -> None:
        client = api.get_client(self._mac_address)
        if client:
            elapsed_time = time() - client["last_seen"]

            # Check if it has been turned off
            if self.is_on() and elapsed_time > self._max_off_time:
                self.turned_off()

            # Check if it has turned on
            elif not self.is_on() and elapsed_time <= self._max_off_time:
                self.turned_on()
        else:
            self.turned_off()