from subprocess import run, CalledProcessError
import logging


devices = []


logger = logging.getLogger(__name__)


class NetworkDevice:
    def __init__(self, ip):
        self.ip = ip
        self.on = False
        devices.append(self)

    def ping_device(self):
        try:
            run(['ping', '-c', '1', '-W', '4', self.ip], check=True)
            self.on = True
        except CalledProcessError:
            self.on = False
        logger.debug('NetworkDevice: ' + self.ip + ' ' + str(self.on))


class NetworkDevices:
    mina = NetworkDevice("192.168.0.248")
    tv = NetworkDevice("192.168.0.2")
    mobile_matteus = NetworkDevice("192.168.0.200")
    mobile_emma = NetworkDevice("192.168.0.201")

    @staticmethod
    def is_someone_home():
        return NetworkDevices.mobile_matteus.on or NetworkDevices.mobile_emma.on

    @staticmethod
    def update():
        for device in devices:
            device.ping_device()
