from .tradfri_gateway import TradfriGateway, Lights, Groups
from .network import Network
from .time import Time, Day, Date
from .luminance import Luminance
from datetime import time

import logging


STATE_NA = "not applicable"
STATE_ON = "on"
STATE_OFF = "off"

logger = logging.getLogger(__name__)


def _calculate_ambient():
    # Only when someone's home
    if Network.is_someone_home():
        # Only when it's dark
        if Luminance.is_dark():
            # Weekends
            if Day.is_day(Day.SATURDAY, Day.SUNDAY):
                if Time.between(time(9), time(2)):
                    return STATE_ON
            # Weekdays
            else:
                if Time.between(time(7, 30), time(2)):
                    return STATE_ON

    return STATE_OFF


class Controller:
    def __init__(self, name):
        self.state = STATE_NA
        self.brightness = None
        self.name = name

    @staticmethod
    def update_all():
        logger.debug('Updating controllers')
        for controller in controllers:
            logger.debug('Updating controller: ' + controller.name)
            last_state = controller.state
            last_brightness = controller.brightness

            controller.state = STATE_OFF
            controller.update()

            # Controller state updated
            if controller.state != last_state:
                logger.debug('State changed from ' +
                             last_state + ' -> ' + controller.state)
                if controller.state == STATE_ON:
                    controller.turn_on()
                elif controller.state == STATE_OFF:
                    controller.turn_off()

            # Brightness updated
            if controller.brightness != last_brightness:
                controller.dim()

    def turn_on(self):
        logger.info('Turning on ' + self.name)
        TradfriGateway.turn_on(self._get_light_or_group())
        # Dim to correct value
        if self.brightness:
            self.dim(transition_time=0)

    def turn_off(self):
        logger.info('Turning off ' + self.name)
        TradfriGateway.turn_off(self._get_light_or_group())

    def dim(self, transition_time=60):
        if self.state == STATE_ON:
            logger.info('Dimming {} to {}'.format(self.name, self.brightness))
            TradfriGateway.dim(self._get_light_or_group(),
                               self.brightness, transition_time=transition_time)

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
            # Always on when the sun has set
            if Luminance.is_sun_down():
                logger.debug('ControlMatteus.update(): It\'s dark')
                self.state = STATE_ON

        # Update dim
        if Time.between(time(10), time(19)):
            self.brightness = 254
        elif Time.between(time(19), time(21)):
            self.brightness = 150
        elif Time.between(time(21), time(22)):
            self.brightness = 70
        else:
            self.brightness = 1

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
        # Only when Matteus is home, computer is turned on, and between 08 and 03
        if (Network.mobile_matteus.is_on() or Network.is_guest_home()) and Network.mina.is_on() and Time.between(time(8), time(3)):
            logger.debug('ControlMonitor.update(): Matteus is home')
            # Always on when it's dark outside
            if Luminance.is_dark():
                logger.debug('ControlMonitor.update(): It\'s dark outside')
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
        else:  # Regular lights
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
            if Luminance.is_sun_down():
                self.state = _calculate_ambient()


class ControlMatteusTurnOff(Controller):
    """Will only turn off lights in Matteus if I leave home. Will never turn it back on."""

    def __init__(self):
        super().__init__('Turn off Matteus')

    def _get_light_or_group(self):
        return [Lights.led_strip, Groups.matteus, Lights.bamboo]

    def update(self):
        if Network.mobile_matteus.is_on() or Network.is_guest_home():
            if not TradfriGateway.isOn(Lights.ac):
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
            if Luminance.is_dark():
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
