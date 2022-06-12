from enum import Enum
from typing import List

from ..smart_interfaces.devices import Devices
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from ..utils.time import Date
from .controller import Controller, calculate_ambient


class ControlMicro(Controller):
    def __init__(self) -> None:
        super().__init__("Kitchen Micro")

    def _get_interfaces(self) -> List[Enum]:
        # Only active when we don't have Christmas lights
        if not Date.has_christmas_lights():
            return [Devices.window, Devices.micro]
        else:
            return []

    def update(self):
        if Sensors.kitchen_light.is_level_or_below(LightLevels.fully_dark):
            self.state = calculate_ambient()
