from subprocess import run, CalledProcessError
import logging


devices = []


logger = logging.getLogger(__name__)
OFF_TIMES_DEFAULT = 10
NEXT_CHECK_IN_DEFAULT = 10
TIMEOUT_DEFAULT = 4


class NetworkDevice:
    """Checks if a device is on or not."""
    def __init__(self, ip, off_times = OFF_TIMES_DEFAULT, timeout = TIMEOUT_DEFAULT):
        self.ip = ip
        self.next_check_in = 0
        self.off_times = off_times
        self.off_times_check = off_times
        self.timeout = str(timeout)
        devices.append(self)

    def is_on(self):
        """
        Check if the device is turned on
        :return: False if the 5 or more last pings were unsuccessful (read device turned off or unavailable.
        Otherwise return True. This is used since sometimes a Wifi device will won't respond before the timeout.
        """
        return self.off_times < self.off_times_check

    def ping_device(self):
        if self.next_check_in == 0:
            try:
                run(['ping', '-c', '1', '-W', self.timeout, self.ip], check=True)
                self.off_times = 0
                self.next_check_in = NEXT_CHECK_IN_DEFAULT
            except CalledProcessError:
                self.off_times += 1

            logger.debug('NetworkDevice: ' + self.ip + ' ' + str(self.off_times))
        else:
            self.next_check_in -= 1


class NetworkDevices:
    mina = NetworkDevice("192.168.0.248", off_times=2, timeout=1)
    tv = NetworkDevice("192.168.0.2", off_times=5, timeout=3)
    mobile_matteus = NetworkDevice("192.168.0.200", off_times=15, timeout=4)
    mobile_emma = NetworkDevice("192.168.0.201", off_times=30, timeout=6)

    @staticmethod
    def is_someone_home():
        return NetworkDevices.mobile_matteus.is_on() or NetworkDevices.mobile_emma.is_on()

    @staticmethod
    def update():
        for device in devices:
            device.ping_device()
