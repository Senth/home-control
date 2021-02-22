from typing import List, Union
from .devices import Devices
from .groups import Groups
from .interface import Interface


class SmartInterfaces:
    @staticmethod
    def get_interfaces(names: Union[List[str], str]) -> List[Interface]:
        """Return all interfaces with the specified name(s)"""
        interfaces: List[Interface] = []

        # Single name
        if isinstance(names, str):
            found = SmartInterfaces._find_interface(names)
            if found:
                interfaces.append(found)
        # Multiple names
        elif isinstance(names, list):
            for name in names:
                interfaces.extend(SmartInterfaces.get_interfaces(name))

        return interfaces

    @staticmethod
    def _find_interface(name: str) -> Union[Interface, None]:
        device = Devices.from_name(name)
        if device:
            return device.value

        group = Groups.from_name(name)
        if group:
            return group.value