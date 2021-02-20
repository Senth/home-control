from pytradfri.gateway import Gateway
from pytradfri.group import Group
from typing import List, Union
from .api import Api
from ..interface import Interface


class TradfriGroup(Interface):
    _groups: List[Group] = Api.execute(Gateway().get_groups(), execute_response=True)

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._group: Group
        self._first_update()

    def _first_update(self) -> None:
        for group in TradfriGroup._groups:
            if group.name == self.name:
                self._group = group

    def turn_on(self) -> None:
        if self._group:
            Api.execute(self._group.set_state(True))

    def turn_off(self) -> None:
        if self._group:
            Api.execute(self._group.set_state(False))

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        if self._group:
            normalized_value = Interface.normalize_dim(value)
            Api.execute(self._group.set_dimmer(normalized_value))

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        if self._group:
            normalized_time = Api.seconds_to_tradfri(transition_time)
            Api.execute(self._group.set_xy_color(x, y, transition_time=normalized_time))
