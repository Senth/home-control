from __future__ import annotations

from enum import Enum
from typing import Union

from .hue.group import HueGroup


class Groups(Enum):
    # Rooms
    emma = HueGroup("Emma")
    hallway = HueGroup("Hallway")
    living_room = HueGroup("Living Room")
    kitchen = HueGroup("Kitchen")

    # Zones
    matteus_lights = HueGroup("Matteus lights")

    @staticmethod
    def from_name(name: str) -> Union[Groups, None]:
        # Get from known lights first
        for group in Groups:
            if group.value.name.lower() == name.lower():
                return group
