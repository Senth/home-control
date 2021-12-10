from __future__ import annotations

from enum import Enum
from typing import Union

from .hue.light import HueLight


class Devices(Enum):
    ball_lights = HueLight("Ball lights")
    bamboo = HueLight("Bamboo lamp")
    billy = HueLight("Billy lights")
    ceiling = HueLight("Ceiling")
    cylinder = HueLight("Cylinder lamp")
    hallway_ceiling = HueLight("Hallway ceiling light")
    hallway_painting = HueLight("Hallway painting lights")
    led_strip = HueLight("LED strip")
    micro = HueLight("Micro lights")
    monitor = HueLight("Monitor lights")
    speakers = HueLight("Matteus Speakers")
    window = HueLight("Window lights")
    kitchen_christmas = HueLight("Adventsstake köket")

    @staticmethod
    def from_name(name: str) -> Union[Devices, None]:
        # Get from known lights first
        for device in Devices:
            if device.value.name.lower() == name.lower():
                return device
