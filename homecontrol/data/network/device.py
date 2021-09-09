from __future__ import annotations

from typing import List

from tealprint import TealPrint

from ..stats import Stats


class Device:
    _devices: List[Device] = []

    def __init__(self, name: str, log: bool) -> None:
        self.name: str = name
        self._on: bool = True
        self._log: bool = log
        Device._devices.append(self)

    def turned_on(self) -> None:
        if not self._on:
            TealPrint.info("Device: {} turned on".format(self.name))
            if self._log:
                Stats.log("device", f'{{"power":"on","device":"{self.name}"}}')
            self._on = True

    def turned_off(self) -> None:
        if self._on:
            TealPrint.info("Device: {} turned off".format(self.name))
            if self._log:
                Stats.log("device", f'{{"power":"off","device":"{self.name}"}}')
            self._on = False

    def is_on(self) -> bool:
        return self._on

    def update(self) -> None:
        pass

    @staticmethod
    def update_all() -> None:
        for device in Device._devices:
            device.update()
