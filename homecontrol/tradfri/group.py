from __future__ import annotations
from enum import Enum
from typing import Dict, Union
from pytradfri.gateway import Gateway
from pytradfri.group import Group
from ..config import config
from .common import try_several_times

logger = config.logger


class Groups(Enum):
    matteus = "Matteus"
    living_room = "Vardagsrum"
    cozy = "Vardagsrum (mys)"
    emma = "Emma"
    hall = "Hallen"
    hall_ceiling = "Hallen (tak)"
    hall_sensor = "Hall Motion Sensor Group"
    kitchen = "Köket"

    @staticmethod
    def from_name(group_name: str) -> Union[Groups, None]:
        for group in Groups:
            if group.value.lower() == group_name.lower():
                return group


class GroupHandler:
    def __init__(self, gateway: Gateway) -> None:
        self._gateway = gateway
        self._groups: Dict[Groups, Group] = {}

    def update(self) -> None:
        """Bind all groups from pytradfri

        Args:
            groups (List[Any]): All the groups from pytradfri
        """
        groups = try_several_times(self._gateway.get_groups(), execute_response=True)
        for group in groups:
            if isinstance(group, Group):
                group_enum = Groups.from_name(group.name)
                if group_enum:
                    self._groups[group_enum] = group
                else:
                    logger.debug(f"Didn't find group {group.name} in enum.")

        if len(self._groups) != len(Groups):
            for group in Groups:
                if group not in self._groups:
                    logger.warning(
                        f"No group bound for enum {group.name} with value '{group.value}''"
                    )

    def get_group(self, group: Groups) -> Union[Group, None]:
        """Get the tradfri group from the enum

        Args:
            group (Groups): The group to get

        Returns:
            Union[Group, None]: The group if found, otherwise None
        """
        if group in self._groups:
            return self._groups[group]
