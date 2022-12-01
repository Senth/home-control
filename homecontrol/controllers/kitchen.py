from enum import Enum
from typing import List

from ..smart_interfaces.devices import Devices
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from .controller import Controller, calculate_ambient


class ControlMicro(Controller):
    def __init__(self) -> None:
        super().__init__("Kitchen Micro")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.micro, Devices.kitchen_christmas]

    def update(self):
        if Sensors.kitchen_light.is_level_or_below(LightLevels.fully_dark):
            self.state = calculate_ambient()
