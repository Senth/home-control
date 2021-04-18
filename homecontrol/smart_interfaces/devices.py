from __future__ import annotations

from enum import Enum
from typing import Union

from .hue.light import HueLight


class Devices(Enum):
    ball_lights = HueLight(6, "Ball lights")
    bamboo = HueLight(17, "Bamboo lamp")
    billy = HueLight(9, "Billy lights")
    ceiling = HueLight(16, "Ceiling")
    cylinder = HueLight(10, "Cylinder lamp")
    hallway_ceiling = HueLight(4, "Hallway ceiling light")
    hallway_panting = HueLight(7, "Hallway painting lights")
    # kitchen_advent = TradfriSocket("Adventsstake kök")
    led_strip = HueLight(11, "LED strip")
    micro = HueLight(12, "Micro lights")
    monitor = HueLight(8, "Monitor lights")
    window = HueLight(5, "Window lights")

    @staticmethod
    def from_name(name: str) -> Union[Devices, None]:
        # Get from known lights first
        for device in Devices:
            if device.value.name.lower() == name.lower():
                return device
