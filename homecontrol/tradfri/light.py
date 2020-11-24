from __future__ import annotations
from enum import Enum
from typing import Dict, Union
from pytradfri.device import Device
from pytradfri.gateway import Gateway
from .common import try_several_times
from ..config import config

logger = config.logger


class Lights(Enum):
    window = "Window lights"
    ball = "Ball lights"
    ceiling = "Ceiling light"
    sun_lamp = "Sun lamp"
    led_strip = "LED strip"
    monitor = "Monitor lights"
    billy = "Billy lights"
    bamboo = "Bamboo lamp"
    hall_ceiling = "Hallen Taklampa"
    hall_painting = "Hall light"
    ac = "AC"
    cylinder = "Cylinder lamp"
    micro = "Micro lights"
    emma_star = "Stjärnan lampa"
    emma_billy = "Bokhylla lampa"
    emma_salt = "Salt lampa"
    emma_slinga = "Ljusslinga lampa"

    @staticmethod
    def from_name(light_name: str) -> Union[Lights, None]:
        for light in Lights:
            if light.value.lower() == light_name.lower():
                return light


class LightHandler:
    def __init__(self, gateway: Gateway) -> None:
        self._gateway = gateway
        self._lights: Dict[Lights, Device] = {}

    def update(self) -> None:
        """Bind all the light devices from pytradfri"""
        devices = try_several_times(self._gateway.get_devices(), execute_response=True)
        for device in devices:
            if isinstance(device, Device):
                light = Lights.from_name(device.name)
                if light:
                    self._lights[light] = device
                else:
                    logger.info(f"Didn't find light {device.name} in enum.")

        if len(self._lights) != len(Lights):
            for light in Lights:
                if light not in self._lights:
                    logger.warning(
                        f"No light bound for enum {light.name} with value '{light.value}''"
                    )

    def get_light_device(self, light: Lights) -> Union[Device, None]:
        """Get the tradfri light device from the enum

        Args:
            light (Lights): The light device to get

        Returns:
            Union[Device, None]: The device if found, otherwise None
        """
        if light in self._lights:
            return self._lights[light]