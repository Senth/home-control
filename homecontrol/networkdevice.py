from subprocess import run, CalledProcessError
import logging


devices = []


logger = logging.getLogger(__name__)


class NetworkDevice:
    """Checks if a device is on or not."""
    def __init__(self, ip):
        self.ip = ip
        self.off_times = 5
        devices.append(self)

    def is_on(self):
        """
        Check if the device is turned on
        :return: False if the 5 or more last pings were unsuccessful (read device turned off or unavailable.
        Otherwise return True. This is used since sometimes a Wifi device will won't respond before the timeout.
        """
        return self.off_times < 5

    def ping_device(self):
        try:
            run(['ping', '-c', '1', '-W', '3', self.ip], check=True)
            self.off_times = 0
        except CalledProcessError:
            self.off_times += 1

        logger.debug('NetworkDevice: ' + self.ip + ' ' + str(self.off_times))


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
