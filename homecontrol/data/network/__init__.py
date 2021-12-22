from tealprint import TealPrint

from .device import Device
from .guest_of import GuestOf
from .ip_device import IpDevice
from .unifi_device import UnifiDevice
from .unifi_device import api as _unifi_api


class Network:
    zen = IpDevice(
        ip="192.168.0.249",
        name="Zen",
        updates_every=10,
        off_times=2,
        log=True,
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
        mac_address="fa:2f:79:bf:01:f4",
        log=True,
        max_off_time=240,
    )
    mobile_emma = UnifiDevice(
        name="Mobile Emma",
        mac_address="5e:0b:26:29:41:6d",
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
        return Network.mobile_matteus.is_on() or Network.mobile_emma.is_on() or Network.is_guest_home()

    @staticmethod
    def is_guest_home(*guest_of: GuestOf) -> bool:
        return _unifi_api.is_guest_active(*guest_of)

    @staticmethod
    def update() -> None:
        TealPrint.debug("🔄 Network.update()")
        try:
            _unifi_api.update()
            Device.update_all()
        except Exception:
            TealPrint.error("❗ Exception during Network.update()", print_exception=True)
