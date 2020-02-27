from subprocess import run, CalledProcessError
from pyunifi.controller import Controller
from time import time
from .config import UNIFI_USER, UNIFI_PASSWORD, UNIFI_URL, UNIFI_PORT, UNIFI_SITE_ID
import logging


logger = logging.getLogger(__name__)


class Device:
    _devices = []

    def __init__(self, name):
        self.name = name
        self._on = True
        Device._devices.append(self)

    def turned_on(self):
        logger.info('Device: {} turned on'.format(self.name))
        self._on = True

    def turned_off(self):
        logger.info('Device: {} turned off'.format(self.name))
        self._on = False

    def is_on(self):
        return self._on

    def update(self):
        pass

    @staticmethod
    def update_all():
        for device in Device._devices:
            device.update()


class NetworkDevice(Device):
    """Checks if a device is on or not."""
    def __init__(self, ip, name, updates_every=15, off_times=10, timeout=4):
        super().__init__('{} ({})'.format(name, ip))
        self.ip = ip
        self.next_check_in = 0
        self._off_times = off_times
        self._off_times_check = off_times
        self._updates_every = updates_every
        self._timeout = str(timeout)
        self._last_update = 0

    def update(self):
        # Only update the devices every 15 seconds (we don't want to ping so often)
        elapsed_time = time() - self._last_update
        if elapsed_time >= self._updates_every:
            self.ping_device()
            self._last_update = time()

    def ping_device(self):
        last_off_time = self._off_times

        try:
            run(['ping', '-c', '1', '-W', self._timeout, self.ip], check=True)
            self._off_times = 0
        except CalledProcessError:
            self._off_times += 1

        if last_off_time >= self._off_times_check and self._off_times == 0:
            self.turned_on()
        if last_off_time == self._off_times_check and self._off_times > self._off_times_check:
            self.turned_off()
        else:
            logger.debug('NetworkDevice: ' + self.ip + ' ' + str(self._off_times))


class UnifiDevice(Device):
    def __init__(self, name, mac_address, unifi_api, max_off_time=300):
        super().__init__(name)
        self._mac_address = mac_address
        self._unifi_api = unifi_api
        self._max_off_time = max_off_time

    def update(self):
        client = self._unifi_api.get_client(self._mac_address)
        if client:
            elapsed_time = time() - client['last_seen']

            # Check if it has been turned off
            if self.is_on() and elapsed_time > self._max_off_time:
                self.turned_off()

            # Check if it has turned on
            elif not self.is_on() and elapsed_time <= self._max_off_time:
                self.turned_on()
        else:
            self.turned_off()


class UnifiApi:
    USER_GROUP_OWNER = '5c8e9afdcc133518388e9f98'
    GUEST_ACTIVE_TIME = 300

    def __init__(self):
        self.controller = Controller(
            UNIFI_URL,
            UNIFI_USER,
            UNIFI_PASSWORD,
            port=UNIFI_PORT,
            site_id=UNIFI_SITE_ID,
            ssl_verify=False
        )
        self.clients = {}
        self._last_guest_active_time = 0

    def update(self):
        self._update_clients()

    def get_client(self, mac_address):
        """Tries to find the client with the specified mac address. Returns None if it hasn't been active yet"""
        return self.clients[mac_address]

    def is_guest_active(self):
        """Checks the last 5 minutes"""
        elapsed_time = time() - self._last_guest_active_time
        return elapsed_time <= UnifiApi.GUEST_ACTIVE_TIME

    def _update_clients(self):
        for client in self.controller.get_clients():
            self.clients[client['mac']] = client
            if client['usergroup_id'] != UnifiApi.USER_GROUP_OWNER:
                was_guest_active = self.is_guest_active()
                self._last_guest_active_time = time()

                # Changed state
                if was_guest_active != self.is_guest_active():
                    if self.is_guest_active():
                        logger.info('Guest is home')
                    else:
                        logger.info('Guest went away')

class Network:
    _unifi = UnifiApi()

    mina = NetworkDevice("192.168.0.248", 'Cerina', updates_every=10, off_times=2, timeout=1)
    tv = UnifiDevice('TV', '74:40:be:5a:2d:5e', _unifi, max_off_time=60)
    mobile_matteus = UnifiDevice('Mobile Matteus', '04:d6:aa:62:d5:ae', _unifi, max_off_time=240)
    mobile_emma = UnifiDevice('Mobile Emma', '6c:c7:ec:ee:e2:7f', _unifi, max_off_time=420)

    @staticmethod
    def is_someone_home():
        return Network.mobile_matteus.is_on() or Network.mobile_emma.is_on() or Network.is_guest_home()

    @staticmethod
    def is_guest_home():
        return Network._unifi.is_guest_active()

    @staticmethod
    def update():
        Network._unifi.update()
        Device.update_all()
