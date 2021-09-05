from __future__ import annotations

from enum import Enum
from typing import Union

from .hue.group import HueGroup


class Groups(Enum):
    # Rooms
    emma = HueGroup(5, "Emma")
    hallway = HueGroup(3, "Hallway")
    living_room = HueGroup(1, "Living Room")
    kitchen = HueGroup(4, "Kitchen")

    # Zones
    matteus_lights = HueGroup(7, "Matteus lights")

    @staticmethod
    def from_name(name: str) -> Union[Groups, None]:
        # Get from known lights first
        for group in Groups:
            if group.value.name.lower() == name.lower():
                return group
