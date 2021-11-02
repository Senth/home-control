from datetime import datetime, time
from enum import Enum
from time import sleep
from typing import List, Optional, Union

from tealprint import TealPrint

from .core.entities.color import Color
from .data.network import GuestOf, Network
from .smart_interfaces.devices import Devices
from .smart_interfaces.groups import Groups
from .smart_interfaces.hue.light_sensor import LightLevels
from .smart_interfaces.sensors import Sensors
from .utils.time import Date, Day, Days, Time


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
    def __init__(self, name: str) -> None:
        self.state: States = States.initial
        self.brightness: Union[float, int, None] = None
        self.color: Optional[Color] = None
        self.name = name

    @staticmethod
    def update_all() -> None:
        while True:
            for controller in controllers:
                last_state = controller.state
                last_brightness = controller.brightness

                controller.state = States.off
                controller.update()

                # Controller state updated
                if controller.state != last_state:
                    TealPrint.debug(f"{controller.name}: State changed from {last_state} -> {controller.state}")
                    if controller.state == States.off:
                        controller.turn_off()
                    elif controller.state == States.on:
                        controller.turn_on()

                if controller.color != controller.color:
                    controller.colorize()

                # Brightness updated
                if controller.brightness != last_brightness:
                    controller.dim()

            sleep(1)

    def turn_on(self) -> None:
        TealPrint.info("Turning on " + self.name)
        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_on()
        # Dim to correct value
        if self.brightness:
            self.dim(transition_time=0)

    def turn_off(self) -> None:
        TealPrint.info("Turning off " + self.name)
        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_off()

    def dim(self, transition_time: float = 60):
        if self.state == States.on and self.brightness:
            TealPrint.info(f"Dimming {self.name} to {self.brightness}")
            for interface_enum in self._get_interfaces():
                interface_enum.value.dim(
                    self.brightness,
                    transition_time=transition_time,
                )

    def colorize(self):
        if self.state == States.on:
            TealPrint.info(f"Colorize {self.name} to {self.color}")
            for interface_enum in self._get_interfaces():
                interface_enum.value.color(self.color)

    def _get_interfaces(self) -> List[Enum]:
        TealPrint.error(f"Not implemented {self.name}._get_interfaces()")
        raise RuntimeError("Not implemented _get_interfaces")

    def update(self):
        TealPrint.error(f"Not implemented {self.name}._update()")


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
            if Sensors.light_sensor.is_level_or_below(LightLevels.dark):
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
        super().__init__("Bamboo")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.bamboo]

    def update(self):
        # Only when Matteus or Matteus guest is home
        if not Network.mobile_matteus.is_on() and not Network.is_guest_home(GuestOf.both, GuestOf.matteus):
            return

        if not Time.between(time(15), time(3)):
            return

        # Turn on
        if Sensors.light_sensor.is_level_or_below(LightLevels.partially_dark):
            self.state = States.on

        # Set brightness and color
        if Sensors.light_sensor.is_level_or_below(LightLevels.fully_dark):
            if Time.between(time(15), time(19)):
                self.brightness = 0.6
                self.color = Color.from_xy(0.37, 0.37)
            elif Time.between(time(19), time(22)):
                self.brightness = _calculate_dynamic_brightness(time(19), time(22), 0.6, 0.2)
                self.color = _calculate_dynamic_color(
                    time(19), time(22), Color.from_xy(0.37, 0.37), Color.from_xy(0.45, 0.41)
                )
            elif Time.between(time(22), time(23, 30)):
                self.brightness = 1
                self.color = _calculate_dynamic_color(
                    time(22), time(23, 30), Color.from_xy(0.45, 0.41), Color.from_xy(0.7, 0.3)
                )
            else:
                self.brightness = 1
                self.color = Color.from_xy(0.7, 0.3)
        elif Sensors.light_sensor.is_level_or_below(LightLevels.dark):
            self.brightness = 0.75
            self.color = Color.from_xy(0.36, 0.36)
        elif Sensors.light_sensor.is_level_or_below(LightLevels.partially_dark):
            self.brightness = 0.9
            self.color = Color.from_xy(0.32, 0.32)


class ControlMonitor(Controller):
    def __init__(self) -> None:
        super().__init__("Monitor")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.monitor]

    def update(self):
        if Network.is_matteus_home() and Sensors.light_sensor.is_level_or_below(LightLevels.dark):
            # Stationary Computer
            if Network.zen.is_on() and Time.between(time(7), time(3)):
                self.state = States.on
            # Work laptop
            elif Network.work_matteus.is_on() and Time.between(time(7), time(18)):
                self.state = States.on


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


class ControlAmbient(Controller):
    def __init__(self) -> None:
        super().__init__("Ambient")

    def _get_interfaces(self) -> List[Enum]:
        # Winter lights
        if Date.between((11, 28), (1, 31)):
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
        if Date.between((2, 1), (11, 27)):
            return [Devices.window, Devices.micro]
        else:
            return []

    def update(self):
        if Sensors.light_sensor.is_level_or_below(LightLevels.dark):
            self.state = _calculate_ambient()


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


class ControlLedStripOff(Controller):
    """Will only turn off the LED strip if TV is on and Matteus is the only one home"""

    def __init__(self):
        super().__init__("Turn off LED Strip")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.led_strip]

    def update(self):
        self.state = States.on

        # Only if Matteus is alone home
        if (
            Network.mobile_matteus.is_on()
            and not Network.mobile_emma.is_on()
            and not Network.is_guest_home(GuestOf.both, GuestOf.matteus)
        ):
            # Only if TV is on
            if Network.tv.is_on():
                self.state = States.off

    def turn_on(self):
        pass


class ControlTurnOffEmma(Controller):
    def __init__(self):
        super().__init__("Turn off Emma lights")

    def _get_interfaces(self) -> List[Enum]:
        return [Groups.emma]

    def update(self):
        # Turn off if Emma isn't home and there's no guest
        if Network.mobile_emma.is_on() or Network.is_guest_home(GuestOf.both, GuestOf.emma):
            self.state = States.on

    def turn_on(self):
        pass


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


# class ControlSunLamp(Controller):
#     def __init__(self):
#         super().__init__("Sun Lamp")

#     def _get_interfaces(self) -> List[Enum]:
#         return Lights.sun_lamp

#     def update(self):
#         if Time.between(time(4), time(8)):
#             if Luminance.is_dark():
#                 self.state = States.on


class ControlHallCeiling(Controller):
    def __init__(self):
        super().__init__("Hall Ceiling")
        self.brightness = 1.0

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.hallway_ceiling]

    def update(self):
        if Network.is_someone_home():
            if Sensors.light_sensor.is_level_or_below(LightLevels.dark):
                if Day.is_workday():
                    # Only start at 8 Emma has a guest and Matteus is home
                    if Network.is_matteus_home() and Network.is_guest_home(GuestOf.emma):
                        if Time.between(time(8), time(17)):
                            self.state = States.on
                    elif Time.between(time(10), time(17)):
                        self.state = States.on
                elif Day.is_weekend() and Time.between(time(11), time(17)):
                    self.state = States.on


controllers: List[Controller] = [
    ControlMatteus(),
    ControlBamboo(),
    # ControlMonitor(),
    ControlSpeakers(),
    ControlAmbient(),
    ControlWindows(),
    #     ControlSunLamp(),
    ControlMatteusTurnOff(),
    ControlLedStripOff(),
    ControlTurnOffEmma(),
    ControlTurnOffLights(),
    ControlHallCeiling(),
]


def _calculate_dynamic_brightness(
    time_start: time, time_end: time, brightness_start: float, brightness_end: float
) -> float:
    percentage = Time.percentage_between(time_start, time_end)
    return _diff(brightness_start, brightness_end, percentage)


def _calculate_dynamic_color(time_start: time, time_end: time, color_start: Color, color_end: Color) -> Color:
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
    total_diff = end - start
    return round(start + total_diff * percentage, 2)
