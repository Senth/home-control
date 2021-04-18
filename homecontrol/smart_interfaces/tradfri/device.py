from typing import List

from pytradfri.device import Device
from pytradfri.gateway import Gateway

from ..interface import Interface
from .api import Api


class TradfriDevice(Interface):
    _devices: List[Device] = Api.execute(Gateway().get_devices(), execute_response=True)

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._device: Device
        self._first_update()

    def _first_update(self) -> None:
        for device in TradfriDevice._devices:
            if device.name == self.name:
                self._device = device

    def update(self) -> None:
        if self._device:
            device = Api.execute(self._device.update())
            if isinstance(device, Device):
                self._device = device
        else:
            self._first_update()