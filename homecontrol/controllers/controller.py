from __future__ import annotations

from datetime import time
from enum import Enum
from time import sleep
from typing import List, Optional, Union

from tealprint import TealPrint

from ..core.entities.color import Color
from ..data.network import Network
from ..smart_interfaces.devices import Devices
from ..smart_interfaces.groups import Groups
from ..smart_interfaces.hue.light_sensor import LightLevels
from ..smart_interfaces.sensors import Sensors
from ..utils.time import Date, Day, Days, Time


class States(Enum):
    initial = "initial"
    on = "on"
    off = "off"


def _calculate_ambient() -> States:
    # Only when someone's home
    if Network.is_someone_home():
        # Dark
        if Sensors.light_sensor.is_level_or_below(LightLevels.partially_dark):
            # Weekends
            if Day.is_day(Days.saturday, Days.sunday):
                if Time.between(time(9), time(2)):
                    return States.on
            # Weekdays
            else:
                if Time.between(time(7), time(2)):
                    return States.on

    return States.off


class Controller:
    controllers: List[Controller] = []

    def __init__(self, name: str, only_apply_when_on: bool = False) -> None:
        """
        params:
          only_apply_when_on(bool): Only change dim/color if the light is currently turned on
        """
        self.state: States = States.initial
        self.brightness: Union[float, int, None] = None
        self.color: Optional[Color] = None
        self.name = name
        self.only_apply_when_on = only_apply_when_on
        Controller.controllers.append(self)

    @staticmethod
    def update_all() -> None:
        while True:
            for controller in Controller.controllers:
                last_state = controller.state
                last_brightness = controller.brightness
                last_color = controller.color

                controller.state = States.off
                controller.update()

                # Controller state updated
                if controller.state != last_state:
                    TealPrint.debug(f"{controller.name}: State changed from {last_state} -> {controller.state}")
                    if controller.state == States.off:
                        controller.turn_off()
                    elif controller.state == States.on:
                        controller.turn_on()

                if controller.color != last_color:
                    controller.colorize()

                # Brightness updated
                if controller.brightness != last_brightness:
                    controller.dim()

            sleep(1)

    def turn_on(self) -> None:
        TealPrint.info("⚪ Turning on " + self.name, push_indent=True)

        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_on()
        if self.brightness:
            self.dim(transition_time=0)
        if self.color:
            self.colorize()

        TealPrint.pop_indent()

    def turn_off(self) -> None:
        TealPrint.info("⚫ Turning off " + self.name, push_indent=True)
        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_off()
        TealPrint.pop_indent()

    def dim(self, transition_time: float = 60):
        if self.state == States.on and self.brightness:
            TealPrint.info(f"🔅 Dimming {self.name} to {self.brightness}", push_indent=True)
            for interface_enum in self._get_interfaces():
                if self._should_apply(interface_enum):
                    interface_enum.value.dim(
                        self.brightness,
                        transition_time=transition_time,
                    )
            TealPrint.pop_indent()

    def colorize(self):
        if self.state == States.on and self.color:
            TealPrint.info(f"🚦 Colorize {self.name} to {self.color}", push_indent=True)
            for interface_enum in self._get_interfaces():
                if self._should_apply(interface_enum):
                    interface_enum.value.color(self.color)
            TealPrint.pop_indent()

    def _should_apply(self, interface_enum: Enum) -> bool:
        should_apply = True
        if self.only_apply_when_on:
            TealPrint.verbose(f"❔ {self.name} only apply if it's on", push_indent=True)
            if interface_enum.value.is_on():
                TealPrint.verbose(f"🟢 {self.name}.{interface_enum.value.name} is on")
            else:
                TealPrint.verbose(
                    f"🔴 Not applying... {self.name}.{interface_enum.value.name} is off",
                )
                should_apply = False
            TealPrint.pop_indent()

        return should_apply

    def _get_interfaces(self) -> List[Enum]:
        TealPrint.error(f"❗ Not implemented {self.name}._get_interfaces()")
        raise RuntimeError("❗ Not implemented _get_interfaces")

    def update(self):
        TealPrint.error(f"❗ Not implemented {self.name}._update()")


class ControlAmbient(Controller):
    def __init__(self) -> None:
        super().__init__("Ambient")

    def _get_interfaces(self) -> List[Enum]:
        # Winter lights
        if Date.has_christmas_lights():
            return [
                Devices.ball_lights,
                Devices.window,
                Devices.hallway_painting,
                Groups.kitchen,
            ]
        else:  # Regular lights
            return [Devices.hallway_painting, Devices.ball_lights]

    def update(self):
        self.state = _calculate_ambient()


class ControlWindows(Controller):
    def __init__(self) -> None:
        super().__init__("Windows")

    def _get_interfaces(self) -> List[Enum]:
        # Only active when we don't have Christmas lights
        if not Date.has_christmas_lights():
            return [Devices.window, Devices.micro]
        else:
            return []

    def update(self):
        if Sensors.light_sensor.is_level_or_below(LightLevels.dark):
            self.state = _calculate_ambient()


class ControlHallCeiling(Controller):
    def __init__(self):
        super().__init__("Hall Ceiling")
        self.brightness = 1.0

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.hallway_ceiling]

    def update(self):
        if not Network.is_someone_home():
            return

        if Sensors.light_sensor.is_level_or_above(LightLevels.partially_dark):
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


def calculate_dynamic_brightness(
    time_start: time, time_end: time, brightness_start: float, brightness_end: float
) -> float:
    percentage = Time.percentage_between(time_start, time_end)
    return _diff(brightness_start, brightness_end, percentage)


def calculate_dynamic_color(time_start: time, time_end: time, color_start: Color, color_end: Color) -> Color:
    percentage = Time.percentage_between(time_start, time_end)

    color = Color()

    if color_start.x and color_end.x:
        color.x = _diff(color_start.x, color_end.x, percentage)
    if color_start.y and color_end.y:
        color.y = _diff(color_start.y, color_end.y, percentage)
    if color_start.hue and color_end.hue:
        color.hue = int(_diff(color_start.hue, color_end.hue, percentage))
    if color_start.saturation and color_end.saturation:
        color.saturation = int(_diff(color_start.saturation, color_end.saturation, percentage))
    if color_start.temperature and color_end.temperature:
        color.temperature = int(_diff(color_start.temperature, color_end.temperature, percentage))

    return color


def _diff(start: Union[int, float], end: Union[int, float], percentage: float) -> float:
    if percentage < 0 or percentage > 1:
        TealPrint.error(f"❗ Percentage in _diff({start}, {end}, {percentage}) is out of bounds")
        return start

    total_diff = end - start
    return round(start + total_diff * percentage, 2)
