from ...config import config
from .device import Device
from .guest_of import GuestOf
from .ip_device import IpDevice
from .unifi_device import UnifiDevice
from .unifi_device import api as _unifi_api

_logger = config.logger


class Network:
    mina = IpDevice(
        ip="192.168.0.248",
        name="Cerina",
        updates_every=10,
        off_times=2,
        timeout=1,
    )
    work_matteus = IpDevice(
        ip="192.168.0.247",
        name="Matteus' Work Laptop",
        updates_every=21,
        off_times=3,
        timeout=3,
    )
    tv = IpDevice(
        ip="192.168.0.2",
        name="TV",
        updates_every=30,
        off_times=3,
        timeout=4,
    )
    mobile_matteus = UnifiDevice(
        name="Mobile Matteus",
        mac_address="04:d6:aa:62:d5:ae",
        log=True,
        max_off_time=240,
    )
    mobile_emma = UnifiDevice(
        name="Mobile Emma",
        mac_address="a6:c7:fd:0c:a4:05",
        max_off_time=420,
    )

    @staticmethod
    def is_matteus_home() -> bool:
        return Network.mobile_matteus.is_on()

    @staticmethod
    def is_emma_home() -> bool:
        return Network.mobile_emma.is_on()

    @staticmethod
    def is_someone_home() -> bool:
        return (
            Network.mobile_matteus.is_on()
            or Network.mobile_emma.is_on()
            or Network.is_guest_home()
        )

    @staticmethod
    def is_guest_home(*guest_of: GuestOf) -> bool:
        return _unifi_api.is_guest_active(*guest_of)

    @staticmethod
    def update() -> None:
        _logger.debug("Network.update()")
        try:
            _unifi_api.update()
            Device.update_all()
        except Exception as e:
            _logger.error("Exception during Network.update()", e)
