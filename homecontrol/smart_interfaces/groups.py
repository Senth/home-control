from __future__ import annotations
from enum import Enum
from .tradfri.group import TradfriGroup
from .hue.group import HueGroup
from typing import Union


class Groups(Enum):
    # Rooms
    cozy = TradfriGroup("Vardagsrum (mys)")
    emma = TradfriGroup("Emma")
    hallway = HueGroup(3, "Hallway")
    living_room = HueGroup(1, "Living Room")
    kitchen = TradfriGroup("Köket")
    matteus = TradfriGroup("Matteus")

    # Zones

    @staticmethod
    def from_name(name: str) -> Union[Groups, None]:
        # Get from known lights first
        for group in Groups:
            if group.value.name.lower() == name.lower():
                return group
