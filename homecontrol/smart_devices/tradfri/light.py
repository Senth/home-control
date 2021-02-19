from typing import List, Union
from pytradfri.device import Device
from pytradfri.gateway import Gateway
from ..interface import Interface
from .api import api, try_several_times


class TradfriLight(Interface):
    _devices: List[Device] = try_several_times(
        Gateway().get_devices(), execute_response=True
    )

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._device: Device
        self._first_update()

    def _first_update(self) -> None:
        for device in TradfriLight._devices:
            if device.name == self.name:
                self._device = device

    def turn_on(self) -> None:
        try_several_times(self._device.light_control.set_state(True))

    def turn_off(self) -> None:
        try_several_times(self._device.light_control.set_state(False))

    def toggle(self) -> None:
        self.update()
        new_state = not bool(self._device.light_control.lights[0].state)
        try_several_times(self._device.light_control.set_state(new_state))

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        raise NotImplementedError()

    def update(self) -> None:
        raise NotImplementedError()

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        raise NotImplementedError()
