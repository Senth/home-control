from typing import Union
from .api import Api
from .device import TradfriDevice
from ..interface import Interface


class TradfriLight(TradfriDevice):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def turn_on(self) -> None:
        Api.execute(self._device.light_control.set_state(True))

    def turn_off(self) -> None:
        Api.execute(self._device.light_control.set_state(False))

    def toggle(self) -> None:
        new_state = not self.is_on()
        Api.execute(self._device.light_control.set_state(new_state))

    def is_on(self) -> bool:
        self.update()
        return bool(self._device.light_control.lights[0].state)

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        if self._device.light_control.can_set_dimmer:
            normalized_value = Interface.normalize_dim(value)
            Api.execute(self._device.light_control.set_dimmer(normalized_value))

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        if self._device.light_control.can_set_xy:
            normalized_time = Api.seconds_to_tradfri(transition_time)
            Api.execute(
                self._device.light_control.set_xy_color(
                    x, y, transition_time=normalized_time
                )
            )
