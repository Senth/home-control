from enum import Enum
from typing import List

from ..smart_interfaces.devices import Devices
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from .controller import Controller, calculate_ambient


class ControlWindow(Controller):
    def __init__(self) -> None:
        super().__init__("Living Room Windows")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.window]

    def update(self):
        if Sensors.livingroom_light.is_level_or_below(LightLevels.dark):
            self.state = calculate_ambient()


class ControlBalls(Controller):
    def __init__(self) -> None:
        super().__init__("Balls")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.ball_lights]

    def update(self):
        if Sensors.livingroom_light.is_level_or_below(LightLevels.partially_dark):
            if Sensors.kitchen_light.is_level_or_below(LightLevels.partially_light):
                self.state = calculate_ambient()
