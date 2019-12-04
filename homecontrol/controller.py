from .tradfri_gateway import TradfriGateway, Lights, Groups
from .sun import Sun
from .networkdevice import NetworkDevices
from .weather import Weather
from .time import Time
from datetime import time

import logging


STATE_NA = "not applicable"
STATE_ON = "on"
STATE_OFF = "off"

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, name):
        self.state = STATE_NA
        self.name = name

    @staticmethod
    def update_all():
        logger.debug('Updating controllers')
        for control in controllers:
            logger.debug('Updating control: ' + control.name)
            last_state = control.state
            control.state = STATE_OFF
            control.update()

            if control.state != last_state:
                logger.debug('State changed from ' + last_state + ' -> ' + control.state)
                if control.state == STATE_ON:
                    control.turn_on()
                elif control.state == STATE_OFF:
                    control.turn_off()

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
        return Groups.matteus

    def update(self):
        # Only when Matteus is home and between 10 and 03
        if NetworkDevices.mobile_matteus.is_on() and Time.between(time(10), time(3)):
            logger.debug('ControlMatteus.update(): Matteus is home')
            # Always on when it's dark outside
            if Sun.is_dark():
                logger.debug('ControlMatteus.update(): Sun is down')
                self.state = STATE_ON
            else: # Bright outside
                logger.debug('ControlMatteus.update(): Sun is up')
                # Only turn on when it's cloudy and matteus is by the computer
                if NetworkDevices.mina.is_on() and Weather.is_cloudy():
                    logger.debug('ControlMatteus.update(): Matteus computer is on and it\'s cloudy')
                    self.state = STATE_ON

    def turn_off(self):
        # Don't turn off between 8 and 10
        if not Time.between(time(8), time(10)):
            super().turn_off()


class ControlCozyWinter(Controller):
    def __init__(self):
        super().__init__('Cozy')

    def _get_light_or_group(self):
        return [Groups.cozy, Lights.hall]

    def update(self):
        # Only when someone's home
        if NetworkDevices.is_someone_home():
            # Between 13:00 and 02:00
            if Time.between(time(13), time(2)):
                # When the sun has set
                if Sun.is_dark():
                    self.state = STATE_ON
                # Sun is up
                else:
                    # Cloudy outside
                    if Weather.is_cloudy():
                        self.state = STATE_ON


class ControlEmma(Controller):
    def __init__(self):
        super().__init__('Emma')

    def _get_light_or_group(self):
        return Lights.emma

    def update(self):
        # Only when Emma's home
        if NetworkDevices.mobile_emma.is_on():
            # Between 14 and 22 + sun has set
            if Time.between(time(14), time(22)) and Sun.is_dark():
                self.state = STATE_ON


class ControlLEDStrip(Controller):
    """Will only turn off the LED strip if I leave home. Will never turn it back on."""
    def __init__(self):
        super().__init__('LED Strip')

    def _get_light_or_group(self):
        return Lights.led_strip

    def update(self):
        if NetworkDevices.mobile_matteus.is_on():
            self.state = STATE_ON

    def turn_on(self):
        pass


class ControlHall(Controller):
    def __init__(self):
        super().__init__('Hall')

    def _get_light_or_group(self):
        return Lights.hall

    def update(self):
        # Someone's home
        if NetworkDevices.is_someone_home():
            # 7.30-10.00
            if Time.between(time(7, 30), time(10)):
                # Sun is down or cloudy
                if Sun.is_dark() or Weather.is_cloudy():
                    self.state = STATE_ON


controllers = [
    ControlMatteus(),
    ControlCozyWinter(),
    ControlEmma(),
    ControlLEDStrip(),
    ControlHall(),
]
