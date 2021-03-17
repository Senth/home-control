from .smart_interfaces.devices import Devices
from .smart_interfaces.groups import Groups
from .data.network import Network, GuestOf
from .utils.time import Days, Time, Day, Date
from .data.luminance import Luminance
from .config import config
from time import sleep
from datetime import time
from typing import List, Union
from enum import Enum


class States(Enum):
    initial = "initial"
    on = "on"
    off = "off"


logger = config.logger


def _calculate_ambient() -> States:
    # Only when someone's home
    if Network.is_someone_home():
        # Only when it's dark
        if Luminance.is_dark():
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
                    logger.debug(
                        f"State changed from {last_state} -> {controller.state}"
                    )
                    if controller.state == States.on:
                        controller.turn_on()
                    elif controller.state == States.off:
                        controller.turn_off()

                # Brightness updated
                if controller.brightness != last_brightness:
                    controller.dim()
            sleep(1)

    def turn_on(self) -> None:
        logger.info("Turning on " + self.name)
        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_on()
        # Dim to correct value
        if self.brightness:
            self.dim(transition_time=0)

    def turn_off(self) -> None:
        logger.info("Turning off " + self.name)
        for interface_enum in self._get_interfaces():
            interface_enum.value.turn_off()

    def dim(self, transition_time: float = 60):
        if self.state == States.on and self.brightness:
            logger.info(f"Dimming {self.name} to {self.brightness}")
            for interface_enum in self._get_interfaces():
                interface_enum.value.dim(
                    self.brightness,
                    transition_time=transition_time,
                )

    def _get_interfaces(self) -> List[Enum]:
        logger.error(f"Not implemented {self.name}._get_interfaces()")
        raise RuntimeError("Not implemented _get_interfaces")

    def update(self):
        logger.error(f"Not implemented {self.name}._update()")


class ControlMatteus(Controller):
    def __init__(self):
        super().__init__("Matteus")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.billy, Devices.cylinder]

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if (
            Network.mobile_matteus.is_on()
            or Network.is_guest_home(GuestOf.both, GuestOf.matteus)
        ) and Time.between(time(10), time(3)):
            # On when it's dark
            if Luminance.is_dark():
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


class ControlMonitor(Controller):
    def __init__(self) -> None:
        super().__init__("Monitor")

    def _get_interfaces(self) -> List[Enum]:
        return [Devices.monitor]

    def update(self):
        if Network.is_matteus_home() and Luminance.is_dark():
            # Stationary Computer
            if Network.mina.is_on() and Time.between(time(7), time(3)):
                self.state = States.on
            # Work laptop
            elif Network.work_matteus.is_on() and Time.between(time(7), time(18)):
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
                Devices.hallway_panting,
                Groups.kitchen,
            ]
        else:  # Regular lights
            return [Devices.hallway_panting, Devices.ball_lights]

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
        if Luminance.is_sun_down():
            self.state = _calculate_ambient()


class ControlMatteusTurnOff(Controller):
    """Will only turn off lights in Matteus if I leave home. Will never turn it back on."""

    def __init__(self) -> None:
        super().__init__("Turn off Matteus")

    def _get_interfaces(self) -> List[Enum]:
        return [Groups.matteus]

    def update(self):
        if Network.mobile_matteus.is_on() or Network.is_guest_home(
            GuestOf.both, GuestOf.matteus
        ):
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
        return []  # TODO turn off emma

    def update(self):
        # Turn off if Emma isn't home and there's no guest
        if Network.mobile_emma.is_on() or Network.is_guest_home(
            GuestOf.both, GuestOf.emma
        ):
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
            if Time.between(time(11), time(17)):
                if Luminance.is_dark():
                    self.state = States.on


controllers: List[Controller] = [
    ControlMatteus(),
    ControlMonitor(),
    ControlAmbient(),
    ControlWindows(),
    #     ControlSunLamp(),
    ControlMatteusTurnOff(),
    ControlLedStripOff(),
    ControlTurnOffEmma(),
    ControlTurnOffLights(),
    ControlHallCeiling(),
]
