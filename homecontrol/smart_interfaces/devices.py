from __future__ import annotations
from enum import Enum
from typing import Union
from .tradfri.light import TradfriLight
from .tradfri.socket import TradfriSocket
from .hue.light import HueLight


class Devices(Enum):
    ac = TradfriSocket("AC")
    ball = TradfriSocket("Ball lights")
    bamboo = TradfriLight("Bamboo lamp")
    billy = TradfriSocket("Billy lights")
    ceiling = TradfriLight("Ceiling light")
    cylinder = TradfriLight("Cylinder lamp")
    hall_ceiling = HueLight(4, "Hallen taklampa")
    hall_painting = TradfriSocket("Hall light")
    kitchen_advent = TradfriSocket("Adventsstake kök")
    led_strip = TradfriSocket("LED strip")
    micro = TradfriSocket("Micro lights")
    monitor = TradfriSocket("Monitor lights")
    sun_lamp = TradfriSocket("Sun lamp")
    window = TradfriSocket("Window lights")

    @staticmethod
    def from_name(name: str) -> Union[Devices, None]:
        # Get from known lights first
        for device in Devices:
            if device.value.name.lower() == name.lower():
                return device
