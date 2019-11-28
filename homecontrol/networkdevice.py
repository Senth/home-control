from subprocess import run, CalledProcessError
import logging


devices = []


logger = logging.getLogger(__name__)


class NetworkDevice:
    """Checks if a device is on or not. It will save the last 5 states and only if all 5 states are equal to off
    the is_on() function will return False."""
    def __init__(self, ip):
        self.ip = ip
        self.on = False
        self.states = []
        devices.append(self)

    def is_on(self):
        """
        Check if the device is turned on
        :return: False if the 5 last pings were unsuccessful (read device turned off or unavailable.
        Otherwise return True. This is used since sometimes a Wifi device will won't respond before the timeout.
        """
        for state in self.states:
            if state:
                return True
        return False

    def ping_device(self):
        try:
            run(['ping', '-c', '1', '-W', '3', self.ip], check=True)
            self.states.clear()
            self.states.append(True)
        except CalledProcessError:
            self.states.append(False)

            # Only save last 5 states
            if len(self.states) > 5:
                self.states.pop(0)

        logger.debug('NetworkDevice: ' + self.ip + ' ' + str(self.states))


class NetworkDevices:
    mina = NetworkDevice("192.168.0.248")
    tv = NetworkDevice("192.168.0.2")
    mobile_matteus = NetworkDevice("192.168.0.200")
    mobile_emma = NetworkDevice("192.168.0.201")

    @staticmethod
    def is_someone_home():
        return NetworkDevices.mobile_matteus.is_on() or NetworkDevices.mobile_emma.is_on()

    @staticmethod
    def update():
        for device in devices:
            device.ping_device()
