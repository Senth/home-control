from datetime import time
from enum import Enum
from typing import List

from ..data.network import Network
from ..smart_interfaces.devices import Devices
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from ..utils.time import Day, Time
from .controller import Controller, States, calculate_ambient


class ControlHallCeiling(Controller):
    def __init__(self):
        super().__init__("Hall Ceiling")
        self.brightness = 1.0

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.hallway_ceiling]

    def update(self):
        if not Network.is_someone_home():
            return

        if Sensors.livingroom_light.is_level_or_above(LightLevels.partially_dark):
            return

        if Day.is_workday():
            if (Network.is_matteus_home() and Network.is_guest_home()) or (
                Network.is_matteus_home() and not Network.is_emma_home()
            ):
                if Time.between(time(8), time(17)):
                    self.state = States.on
            elif Time.between(time(10), time(17)):
                self.state = States.on
        elif Day.is_weekend() and Time.between(time(11), time(17)):
            self.state = States.on


class ControlPainting(Controller):
    def __init__(self) -> None:
        super().__init__("Painting")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.ball_lights]

    def update(self):
        if Sensors.livingroom_light.is_level_or_below(LightLevels.partially_dark):
            if Sensors.kitchen_light.is_level_or_below(LightLevels.partially_dark):
                self.state = calculate_ambient()
