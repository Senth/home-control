from .tradfri.tradfri_gateway import TradfriGateway, LightsOrGroups
from .tradfri.light import Lights
from .tradfri.group import Groups
from .network import Network
from .time import Days, Time, Day, Date
from .luminance import Luminance
from .config import config
from datetime import time
from typing import Any, List, Union
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
                if Time.between(time(7, 30), time(2)):
                    return States.on

    return States.off


class Controller:
    def __init__(self, name: str) -> None:
        self.state: States = States.initial
        self.brightness: Union[int, None] = None
        self.name = name

    @staticmethod
    def update_all() -> None:
        logger.debug("Updating controllers")
        for controller in controllers:
            logger.debug("Updating controller: " + controller.name)
            last_state = controller.state
            last_brightness = controller.brightness

            controller.state = States.off
            controller.update()

            # Controller state updated
            if controller.state != last_state:
                logger.debug(f"State changed from {last_state} -> {controller.state}")
                if controller.state == States.on:
                    controller.turn_on()
                elif controller.state == States.off:
                    controller.turn_off()

            # Brightness updated
            if controller.brightness != last_brightness:
                controller.dim()

    def turn_on(self) -> None:
        logger.info("Turning on " + self.name)
        TradfriGateway.turn_on(self._get_light_or_group())
        # Dim to correct value
        if self.brightness:
            self.dim(transition_time=0)

    def turn_off(self) -> None:
        logger.info("Turning off " + self.name)
        TradfriGateway.turn_off(self._get_light_or_group())

    def dim(self, transition_time: float = 60):
        if self.state == States.on and self.brightness:
            logger.info(f"Dimming {self.name} to {self.brightness}")
            TradfriGateway.dim(
                self._get_light_or_group(),
                self.brightness,
                transition_time=transition_time,
            )

    def _get_light_or_group(self) -> LightsOrGroups:
        logger.error(f"Not implemented {self.name}._get_light_or_group()")
        raise RuntimeError("Not implemented _get_light_or_group")

    def update(self):
        logger.error(f"Not implemented {self.name}._update()")


class ControlMatteus(Controller):
    def __init__(self):
        super().__init__("Matteus")

    def _get_light_or_group(self):
        return [Lights.cylinder, Lights.billy]

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if (Network.mobile_matteus.is_on() or Network.is_guest_home()) and Time.between(
            time(10), time(3)
        ):
            logger.debug("ControlMatteus.update(): Matteus is home")
            # Always on when the sun has set
            if Luminance.is_sun_down():
                logger.debug("ControlMatteus.update(): Sun is down")
                self.state = States.on

        # Update dim
        if Time.between(time(10), time(19)):
            self.brightness = 180
        elif Time.between(time(19), time(21)):
            self.brightness = 130
        elif Time.between(time(21), time(22)):
            self.brightness = 70
        else:
            self.brightness = 1

    def turn_off(self):
        # Don't turn off between 8 and 10
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlMonitor(Controller):
    def __init__(self) -> None:
        super().__init__("Monitor")

    def _get_light_or_group(self):
        return Lights.monitor

    def update(self):
        # Only when Matteus is home, computer is turned on, and between 08 and 03
        if (
            (Network.mobile_matteus.is_on() or Network.is_guest_home())
            and Network.mina.is_on()
            and Time.between(time(8), time(3))
        ):
            logger.debug("ControlMonitor.update(): Matteus is home")
            # Always on when it's dark outside
            if Luminance.is_dark():
                logger.debug("ControlMonitor.update(): It's dark outside")
                self.state = States.on

    def turn_off(self):
        # Don't turn off between 8 and 10
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlAmbient(Controller):
    def __init__(self) -> None:
        super().__init__("Ambient")

    def _get_light_or_group(self):
        # Winter lights
        if Date.between((11, 28), (1, 31)):
            return [Groups.cozy, Lights.hall_painting, Groups.kitchen]
        else:  # Regular lights
            return [Lights.hall_painting, Lights.ball]

    def update(self):
        self.state = _calculate_ambient()


class ControlWindows(Controller):
    def __init__(self) -> None:
        super().__init__("Windows")

    def _get_light_or_group(self):
        return [Lights.window, Lights.micro]

    def update(self):
        # Only active when it's not winter
        if Date.between((2, 1), (11, 27)):
            if Luminance.is_sun_down():
                self.state = _calculate_ambient()


class ControlMatteusTurnOff(Controller):
    """Will only turn off lights in Matteus if I leave home. Will never turn it back on."""

    def __init__(self) -> None:
        super().__init__("Turn off Matteus")

    def _get_light_or_group(self) -> List[Any]:
        return [Lights.led_strip, Groups.matteus, Lights.bamboo]

    def update(self):
        if Network.mobile_matteus.is_on() or Network.is_guest_home():
            # if not TradfriGateway.isOn(Lights.ac):
            self.state = States.on

    def turn_on(self):
        pass


class ControlLedStripOff(Controller):
    """Will only turn off the LED strip if TV is on and Matteus is the only one home"""

    def __init__(self):
        super().__init__("Turn off LED Strip")

    def _get_light_or_group(self):
        return Lights.led_strip

    def update(self):
        self.state = States.on

        # Only if Matteus is alone home
        if (
            Network.mobile_matteus.is_on()
            and not Network.mobile_emma.is_on()
            and not Network.is_guest_home()
        ):
            # Only if TV is on
            if Network.tv.is_on():
                self.state = States.off

    def turn_on(self):
        pass


class ControlTurnOffEmma(Controller):
    def __init__(self):
        super().__init__("Turn off Emma lights")

    def _get_light_or_group(self):
        return Groups.emma

    def update(self):
        # Turn off if Emma isn't home and there's no guest
        if Network.mobile_emma.is_on() or Network.is_guest_home():
            self.state = States.on

    def turn_on(self):
        pass


class ControlTurnOffLights(Controller):
    """Will only turn off lights (when we leave home if some lights were turned on manually)"""

    def __init__(self):
        super().__init__("Turn off all lights")

    def _get_light_or_group(self):
        return [Groups.cozy, Lights.hall_painting, Lights.ceiling]

    def update(self):
        if Network.is_someone_home():
            self.state = States.on

    def turn_on(self):
        pass


# class ControlSunLamp(Controller):
#     def __init__(self):
#         super().__init__("Sun Lamp")

#     def _get_light_or_group(self):
#         return Lights.sun_lamp

#     def update(self):
#         if Time.between(time(4), time(8)):
#             if Luminance.is_dark():
#                 self.state = States.on


class ControlHallCeiling(Controller):
    def __init__(self):
        super().__init__("Hall Ceiling")

    def _get_light_or_group(self) -> LightsOrGroups:
        return Lights.hall_ceiling

    def update(self):
        if Time.between(time(11), time(17)):
            if Luminance.is_dark():
                self.brightness = 255
                self.state = States.on


controllers = [
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
