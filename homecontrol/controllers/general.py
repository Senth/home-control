from datetime import datetime, time, timedelta
from enum import Enum
from typing import List, Optional

from ..data.network import Network
from ..smart_interfaces.devices import Devices
from ..smart_interfaces.groups import Groups
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from ..utils.time import Date, Time
from .controller import Controller, States


class ControlTurnOffLights(Controller):
    """Will only turn off lights (when we leave home if some lights were turned on manually)"""

    def __init__(self):
        super().__init__("Turn off all lights")

    def _get_interfaces(self) -> List[Enum]:
        return [Groups.living_room, Groups.kitchen, Groups.hallway]

    def update(self):
        if Network.is_someone_home():
            self.state = States.on

    def turn_on(self):
        pass


class ControlChristmasLightsWhenNotHome(Controller):
    """Turn on Christmas decorations when no-one is home"""

    def __init__(self) -> None:
        super().__init__("Christmas Lights when not home")
        self.delayed_turn_on: Optional[datetime] = None

    def _get_interfaces(self) -> List[Enum]:
        if Date.has_christmas_lights():
            return [Devices.billy, Devices.kitchen_christmas, Devices.window]
        else:
            return []

    def update(self) -> None:
        if not Date.has_christmas_lights():
            return

        if Network.is_someone_home():
            return

        # During light hours
        if Time.between(time(9), time(14)):
            return

        # During the night
        if Time.between(time(23), time(7)):
            return

        if Sensors.livingroom_light.is_level_or_above(LightLevels.partially_dark):
            return

        # Start delayed turn on
        if not self.delayed_turn_on:
            self.delayed_turn_on = datetime.now()
        elif datetime.now() - self.delayed_turn_on > timedelta(minutes=1):
            self.state = States.on

    def turn_off(self) -> None:
        """Don't turn off if it was because someone came home. Then we want to leave it on"""
        if not Network.is_someone_home():
            super().turn_off()
