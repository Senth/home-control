from __future__ import annotations
from enum import Enum
from homecontrol.smart_devices.tradfri.group import TradfriGroup
from typing import Union


class Groups(Enum):
    cozy = TradfriGroup("Vardagsrum (mys)")
    emma = TradfriGroup("Emma")
    hall = TradfriGroup("Hallen")
    hall_ceiling = TradfriGroup("Hallen (tak)")
    hall_sensor = TradfriGroup("Hall Motion Sensor Group")
    kitchen = TradfriGroup("Köket")
    living_room = TradfriGroup("Vardagsrum")
    matteus = TradfriGroup("Matteus")

    @staticmethod
    def from_name(name: str) -> Union[Groups, None]:
        # Get from known lights first
        for group in Groups:
            if group.value.name.lower() == name.lower():
                return group