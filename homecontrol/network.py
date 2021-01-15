from __future__ import annotations
from subprocess import run, CalledProcessError, DEVNULL
from typing import Any, Dict, List, Union
from pyunifi.controller import Controller
from time import time
from .config import config
import sys
from .stats import Stats


logger = config.logger


class Device:
    _devices: List[Device] = []

    def __init__(self, name: str, log: bool) -> None:
        self.name: str = name
        self._on: bool = True
        self._log: bool = log
        Device._devices.append(self)

    def turned_on(self) -> None:
        if not self._on:
            logger.info("Device: {} turned on".format(self.name))
            self._on = True
            if self._log:
                Stats.log(self.name, "on")

    def turned_off(self) -> None:
        if self._on:
            logger.info("Device: {} turned off".format(self.name))
            self._on = False
            if self._log:
                Stats.log(self.name, "off")

    def is_on(self) -> bool:
        return self._on

    def update(self) -> None:
        pass

    @staticmethod
    def update_all() -> None:
        for device in Device._devices:
            device.update()


class NetworkDevice(Device):
    """Checks if a device is on or not."""

    def __init__(
        self,
        ip: str,
        name: str,
        log: bool = False,
        updates_every: int = 15,
        off_times: int = 10,
        timeout: int = 4,
    ):
        super().__init__(f"{name} ({ip})", log)
        self.ip = ip
        self.next_check_in = 0
        self._off_times = off_times
        self._off_times_check = off_times
        self._updates_every = updates_every
        self._timeout = str(timeout)
        self._last_update = 0

    def update(self) -> None:
        # Only update the devices every 15 seconds (we don't want to ping so often)
        elapsed_time = time() - self._last_update
        if elapsed_time >= self._updates_every:
            self._ping_device()
            self._last_update = time()

    def _ping_device(self) -> None:
        last_off_time = self._off_times

        try:
            out = DEVNULL

            if config.debug:
                out = sys.stdout

            run(
                ["ping", "-c", "1", "-W", self._timeout, self.ip],
                check=True,
                stdout=out,
            )
            self._off_times = 0
        except CalledProcessError:
            self._off_times += 1

        if last_off_time >= self._off_times_check and self._off_times == 0:
            self.turned_on()
        if (
            last_off_time == self._off_times_check
            and self._off_times > self._off_times_check
        ):
            self.turned_off()
        else:
            logger.debug(f"NetworkDevice: {self.ip} {self._off_times}")


class UnifiDevice(Device):
    def __init__(
        self,
        name: str,
        mac_address: str,
        unifi_api: UnifiApi,
        log: bool = False,
        max_off_time: int = 300,
    ) -> None:
        super().__init__(name, log)
        self._mac_address = mac_address
        self._unifi_api = unifi_api
        self._max_off_time = max_off_time

    def update(self) -> None:
        client = self._unifi_api.get_client(self._mac_address)
        if client:
            elapsed_time = time() - client["last_seen"]

            # Check if it has been turned off
            if self.is_on() and elapsed_time > self._max_off_time:
                self.turned_off()

            # Check if it has turned on
            elif not self.is_on() and elapsed_time <= self._max_off_time:
                self.turned_on()
        else:
            self.turned_off()


class UnifiApi:
    def __init__(self) -> None:
        self.controller = Controller(
            config.unifi.host,
            config.unifi.username,
            config.unifi.password,
            port=config.unifi.port,
            site_id=config.unifi.site_id,
            ssl_verify=True,
        )
        self.clients: Dict[str, Any] = {}
        self._last_guest_active_time = 0

    def update(self) -> None:
        self._update_clients()

    def get_client(self, mac_address: str) -> Union[Any, None]:
        """Tries to find the client with the specified mac address. Returns None if it hasn't been active yet"""
        if mac_address in self.clients:
            return self.clients[mac_address]

    def is_guest_active(self):
        """Checks the last X minutes"""
        elapsed_time = time() - self._last_guest_active_time
        return elapsed_time <= config.unifi.guest_inactive_time

    def _update_clients(self):
        logger.debug("Getting UNIFI clients")
        for client in self.controller.get_clients():
            # logger.debug("Client info: " + str(client))
            self.clients[client["mac"]] = client
            if (
                "usergroup_id" not in client
                or client["usergroup_id"] != config.unifi.usergroup_owner
            ):
                was_guest_active = self.is_guest_active()
                self._last_guest_active_time = time()

                # Changed state
                if was_guest_active != self.is_guest_active():
                    if self.is_guest_active():
                        logger.info("Guest is home")
                    else:
                        logger.info("Guest went away")


class Network:
    _unifi = UnifiApi()

    mina = NetworkDevice(
        "192.168.0.248", "Cerina", updates_every=10, off_times=2, timeout=1
    )
    work_matteus = NetworkDevice(
        "192.168.0.247",
        "Matteus' Work Laptop",
        updates_every=21,
        off_times=3,
        timeout=3,
    )
    tv = NetworkDevice("192.168.0.2", "TV", updates_every=30, off_times=3, timeout=4)
    mobile_matteus = UnifiDevice(
        "Mobile Matteus", "04:d6:aa:62:d5:ae", _unifi, log=True, max_off_time=240
    )
    mobile_emma = UnifiDevice(
        "Mobile Emma", "6c:c7:ec:ee:e2:7f", _unifi, max_off_time=420
    )

    @staticmethod
    def is_someone_home() -> bool:
        return (
            Network.mobile_matteus.is_on()
            or Network.mobile_emma.is_on()
            or Network.is_guest_home()
        )

    @staticmethod
    def is_guest_home() -> bool:
        return Network._unifi.is_guest_active()

    @staticmethod
    def update() -> None:
        logger.debug("Network.update()")
        Network._unifi.update()
        Device.update_all()
