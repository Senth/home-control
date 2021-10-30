from __future__ import annotations

from typing import Union

from .interface import HueInterface


class HueGroup(HueInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name, "groups", "action")

    @staticmethod
    def find(name: str) -> Union[HueGroup, None]:
        hue_group = HueGroup(name)
        if hue_group.id != HueInterface.INVALID_ID:
            return hue_group
        return None
