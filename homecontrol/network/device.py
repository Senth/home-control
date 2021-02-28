from __future__ import annotations
from typing import List
from ..config import config
from ..stats import Stats

_logger = config.logger


class Device:
    _devices: List[Device] = []

    def __init__(self, name: str, log: bool) -> None:
        self.name: str = name
        self._on: bool = True
        self._log: bool = log
        Device._devices.append(self)

    def turned_on(self) -> None:
        if not self._on:
            _logger.info("Device: {} turned on".format(self.name))
            self._on = True
            if self._log:
                Stats.log(self.name, "on")

    def turned_off(self) -> None:
        if self._on:
            _logger.info("Device: {} turned off".format(self.name))
            self._on = False
            if self._log:
                Stats.log(self.name, "off")

    def is_on(self) -> bool:
        return self._on

    def update(self) -> None:
        pass

    @staticmethod
    def update_all() -> None:
        for device in Device._devices:
            device.update()
