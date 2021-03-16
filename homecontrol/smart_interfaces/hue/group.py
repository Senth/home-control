from __future__ import annotations
from typing import Union
from .interface import HueInterface
from .api import Api


class HueGroup(HueInterface):
    def __init__(self, id: int, name: str) -> None:
        super().__init__(id, name, "groups", "action")

    @staticmethod
    def find(name: str) -> Union[HueGroup, None]:
        name = name.lower()
        groups = Api.get(f"/groups")

        if groups:
            for id, data in groups.items():
                if "name" in data and str(data["name"]).lower() == name:
                    return HueGroup(int(id), str(data["name"]))
