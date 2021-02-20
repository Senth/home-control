from .api import Api
from .device import TradfriDevice


class TradfriSocket(TradfriDevice):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def turn_on(self) -> None:
        Api.execute(self._device.socket_control.set_state(True))

    def turn_off(self) -> None:
        Api.execute(self._device.socket_control.set_state(False))

    def toggle(self) -> None:
        new_state = not self.is_on()
        Api.execute(self._device.socket_control.set_state(new_state))

    def is_on(self) -> bool:
        self.update()
        return bool(self._device.socket_control.sockets[0].state)
