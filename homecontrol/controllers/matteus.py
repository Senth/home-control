from datetime import datetime, time, timedelta
from enum import Enum
from typing import List

from tealprint import TealPrint

from ..core.entities.color import Color
from ..data.network import GuestOf, Network
from ..smart_interfaces.devices import Devices
from ..smart_interfaces.groups import Groups
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from ..utils.time import Time
from .controller import (
    Controller,
    States,
    calculate_dynamic_brightness,
    calculate_dynamic_color,
)


class ControlMatteus(Controller):
    def __init__(self):
        super().__init__("Matteus")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.billy, Devices.cylinder]

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if (Network.mobile_matteus.is_on() or Network.is_guest_home(GuestOf.both, GuestOf.matteus)) and Time.between(
            time(10), time(3)
        ):
            # On when it's dark
            if Sensors.kitchen_light.is_level_or_below(LightLevels.dark):
                self.state = States.on

        # Update dim
        if Time.between(time(10), time(19)):
            self.brightness = 0.7
        elif Time.between(time(19), time(21)):
            self.brightness = 0.5
        elif Time.between(time(21), time(22)):
            self.brightness = 0.25
        else:
            self.brightness = 1  # Lowest value

    def turn_off(self):
        # Don't turn off between 8 and 10 (Because we've turned it on)
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlBamboo(Controller):
    def __init__(self) -> None:
        super().__init__("Bamboo", only_apply_when_on=True)
        self.default_color = Color.from_xy(0.43, 0.39)

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.bamboo]

    def update(self):
        # Only when Matteus or Matteus guest is home
        if not Network.mobile_matteus.is_on() and not Network.is_guest_home(GuestOf.both, GuestOf.matteus):
            return

        if not Time.between(time(15), time(3)):
            return

        # Turn on
        if Sensors.kitchen_light.is_level_or_below(LightLevels.dark):
            self.state = States.on

        # Set brightness and color
        self.color = self.default_color
        if Sensors.kitchen_light.is_level_or_below(LightLevels.fully_dark):
            # 15 - 19
            if Time.between(time(15), time(19)):
                self.brightness = 0.6
            # 19 - 22
            elif Time.between(time(19), time(22)):
                self.brightness = calculate_dynamic_brightness(time(19), time(22), 0.6, 0.2)
                self.color = calculate_dynamic_color(time(19), time(22), self.default_color, Color.from_xy(0.48, 0.39))
            # 22:00 - 23:30
            elif Time.between(time(22), time(23, 30)):
                self.brightness = 1
                self.color = calculate_dynamic_color(
                    time(22), time(23, 30), Color.from_xy(0.48, 0.39), Color.from_xy(0.67, 0.31)
                )
            else:
                self.brightness = 1
                self.color = Color.from_xy(0.7, 0.3)
        elif Sensors.kitchen_light.is_level_or_below(LightLevels.dark):
            self.brightness = 0.65


class ControlSpeakers(Controller):
    def __init__(self) -> None:
        self.turn_on_with_computer = True
        super().__init__("Speakers")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.speakers]

    def update(self):
        if Network.is_matteus_home() or Network.is_someone_home():
            if Network.zen.is_on() and self.turn_on_with_computer:
                self.state = States.on


class ControlMatteusTurnOff(Controller):
    """Will only turn off lights in Matteus if I leave home. Will never turn it back on."""

    def __init__(self) -> None:
        super().__init__("Turn off Matteus")

    def _get_interfaces(self) -> List[Enum]:
        return [Groups.matteus_lights]

    def update(self):
        if Network.mobile_matteus.is_on() or Network.is_guest_home(GuestOf.both, GuestOf.matteus):
            self.state = States.on

    def turn_on(self):
        pass


class ControlLedStrip(Controller):
    MAX_DIFF_TIME = timedelta(hours=1, minutes=30)

    def __init__(self):
        super().__init__("LED Strip")
        self.turned_off_time = datetime(2010, 1, 1)

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.led_strip]

    def update(self):
        self.state = States.on

        # Turn off when not home
        if not Network.is_matteus_home():
            self.state = States.off

        # Turn off when watching TV and home alone
        if (
            Network.tv.is_on()
            and not Network.is_emma_home()
            and not Network.is_guest_home(GuestOf.both, GuestOf.matteus)
        ):
            self.state = States.off

        # Turn off when turning off the stationary computer
        if not Network.zen.is_on():
            self.state = States.off

    def turn_on(self) -> None:
        """Only turn on if it was on recently"""
        TealPrint.verbose(f"💡 {self.name}: Trying to turn it on", push_indent=True)
        diff_time = datetime.now() - self.turned_off_time
        TealPrint.verbose(f"⏲ {diff_time} since stopped, should be max {ControlLedStrip.MAX_DIFF_TIME}")
        TealPrint.pop_indent()
        if diff_time < ControlLedStrip.MAX_DIFF_TIME:
            super().turn_on()

    def turn_off(self) -> None:
        if Devices.led_strip.value.is_on():
            self.turned_off_time = datetime.now()
            super().turn_off()
