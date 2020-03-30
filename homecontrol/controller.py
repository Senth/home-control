from .tradfri_gateway import TradfriGateway, Lights, Groups
from .sun import Sun
from .network import Network
from .weather import Weather
from .time import Time, Day, Date
from datetime import time

import logging


STATE_NA = "not applicable"
STATE_ON = "on"
STATE_OFF = "off"

logger = logging.getLogger(__name__)


def _calculate_ambient():
    # Only when someone's home
    if Network.is_someone_home():
        # Weekends
        if Day.is_day(Day.SATURDAY, Day.SUNDAY):
            if Time.between(time(9), time(2)):
                # Sun has set
                if Sun.is_dark():
                    return STATE_ON
                # Sun is up
                else:
                    # Cloudy outside
                    if Weather.is_cloudy():
                        return STATE_ON
        else:  # Weekdays
            if Time.between(time(7, 30), time(2)):
                # When the sun has set
                if Sun.is_dark():
                    return STATE_ON
                # Sun is up
                else:
                    # Cloudy outside
                    if Weather.is_cloudy():
                        return STATE_ON
    return STATE_OFF


class Controller:
    def __init__(self, name):
        self.state = STATE_NA
        self.name = name

    @staticmethod
    def update_all():
        logger.debug('Updating controllers')
        for controller in controllers:
            logger.debug('Updating controller: ' + controller.name)
            last_state = controller.state
            controller.state = STATE_OFF
            controller.update()

            if controller.state != last_state:
                logger.debug('State changed from ' + last_state + ' -> ' + controller.state)
                if controller.state == STATE_ON:
                    controller.turn_on()
                elif controller.state == STATE_OFF:
                    controller.turn_off()

    def turn_on(self):
        logger.info('Turning on ' + self.name)
        TradfriGateway.turn_on(self._get_light_or_group())

    def turn_off(self):
        logger.info('Turning off ' + self.name)
        TradfriGateway.turn_off(self._get_light_or_group())

    def _get_light_or_group(self):
        logger.error('Not implemented ' + self.name + '._get_light_or_group()')
        return None

    def update(self):
        logger.error('Not implemented ' + self.name + '._update()')


class ControlMatteus(Controller):
    def __init__(self):
        super().__init__('Matteus')

    def _get_light_or_group(self):
        return [Lights.cylinder, Lights.billy]

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if (Network.mobile_matteus.is_on() or Network.is_guest_home()) and Time.between(time(10), time(3)):
            logger.debug('ControlMatteus.update(): Matteus is home')
            # Always on when it's dark outside
            if Sun.is_dark():
                logger.debug('ControlMatteus.update(): Sun is down')
                self.state = STATE_ON

    def turn_off(self):
        # Don't turn off between 8 and 10
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlMonitor(Controller):
    def __init__(self):
        super().__init__('Monitor')

    def _get_light_or_group(self):
        return Lights.monitor

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if (Network.mobile_matteus.is_on() or Network.is_guest_home()) and Time.between(time(8), time(3)):
            logger.debug('ControlMonitor.update(): Matteus is home')
            # Always on when it's dark outside
            if Sun.is_dark():
                logger.debug('ControlMonitor.update(): Sun is down')
                self.state = STATE_ON
            else:  # Bright outside
                logger.debug('ControlMonitor.update(): Sun is up')
                # Only turn on when it's cloudy and matteus is by the computer and during winter
                if Network.mina.is_on() and Weather.is_cloudy() and Date.between((10, 14), (3, 14)):
                    logger.debug('ControlMonitor.update(): Matteus computer is on and it\'s cloudy')
                    self.state = STATE_ON

    def turn_off(self):
        # Don't turn off between 8 and 10
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlAmbient(Controller):
    def __init__(self):
        super().__init__('Ambient')

    def _get_light_or_group(self):
        # Winter lights
        if Date.between((11, 28), (1, 31)):
            return [Groups.cozy, Lights.hall, Lights.micro]
        else: # Regular lights
            return [Lights.hall, Lights.ball]

    def update(self):
        self.state = _calculate_ambient()


class ControlWindows(Controller):
    def __init__(self):
        super().__init__('Windows')

    def _get_light_or_group(self):
        return [Lights.window, Lights.micro]

    def update(self):
        # Only active when it's not winter
        if Date.between((2, 1), (11, 27)):
            if Sun.is_dark():
                self.state = _calculate_ambient()


class ControlMatteusTurnOff(Controller):
    """Will only turn off lights in Matteus if I leave home. Will never turn it back on."""
    def __init__(self):
        super().__init__('Turn off Matteus')

    def _get_light_or_group(self):
        return [Lights.led_strip, Groups.matteus, Lights.bamboo]

    def update(self):
        if Network.mobile_matteus.is_on() or Network.is_guest_home():
            self.state = STATE_ON

    def turn_on(self):
        pass


class ControlLedStripOff(Controller):
    """Will only turn off the LED strip if TV is on and Matteus is the only one home"""
    def __init__(self):
        super().__init__('Turn off LED Strip')

    def _get_light_or_group(self):
        return Lights.led_strip

    def update(self):
        self.state = STATE_ON

        # Only if Matteus is alone home
        if Network.mobile_matteus.is_on() and not Network.mobile_emma.is_on() and not Network.is_guest_home():
            # Only if TV is on
            if Network.tv.is_on():
                self.state = STATE_OFF

    def turn_on(self):
        pass


class ControlTurnOffEmma(Controller):
    def __init__(self):
        super().__init__('Turn off Emma lights')

    def _get_light_or_group(self):
        return Groups.emma

    def update(self):
        # Turn off if Emma isn't home and there's no guest
        if Network.mobile_emma.is_on() or Network.is_guest_home():
            self.state = STATE_ON

    def turn_on(self):
        pass


class ControlTurnOffLights(Controller):
    """Will only turn off lights (when we leave home if some lights were turned on manually)"""
    def __init__(self):
        super().__init__('Turn off all lights')

    def _get_light_or_group(self):
        return [Groups.cozy, Lights.hall, Lights.ceiling]

    def update(self):
        if Network.is_someone_home():
            self.state = STATE_ON

    def turn_on(self):
        pass


class ControlSunLamp(Controller):
    def __init__(self):
        super().__init__('Sun Lamp')

    def _get_light_or_group(self):
        return Lights.sun_lamp

    def update(self):
        if Time.between(time(4), time(8)):
            # If sun is not up or cloudy
            if Sun.is_down() or Weather.is_cloudy():
                self.state = STATE_ON


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
]
