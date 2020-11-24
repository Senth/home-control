from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Union
from pytradfri.gateway import Gateway
from pytradfri.group import Group
from pytradfri.mood import Mood
from ..config import config
from .common import try_several_times, api

logger = config.logger


class Groups(Enum):
    matteus = "Matteus"
    living_room = "Vardagsrum"
    cozy = "Vardagsrum (mys)"
    bamboo = "Bamboo"
    emma = "Emma"
    hall = "Hallen"
    hall_ceiling = "Hallen (tak)"
    matteus_led_strip = "Matteus (LED strip)"
    sun = "Sun"
    kitchen = "Köket"

    @staticmethod
    def from_name(group_name: str) -> Union[Groups, None]:
        for group in Groups:
            if group.value == group_name:
                return group


class GroupHandler:
    def __init__(self, gateway: Gateway) -> None:
        self._gateway = gateway
        self._groups: Dict[Groups, Group] = {}
        self._moods: Dict[Groups, List[Mood]] = {}

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

                    # Get moods for the group
                    self._moods[group_enum] = try_several_times(
                        group.moods(), execute_response=True
                    )

                else:
                    logger.info(f"Didn't find group {group.name} in enum.")

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

    def get_mood(self, group: Groups, mood_name: str) -> Union[Mood, None]:
        """Get the mood for the specified group

        Args:
            group (Group): The group to get the mood from
            mood_name (str): Name of the mood

        Returns:
            Union[Mood, None]: The mood if found, otherwise None
        """
        if group in self._moods:
            for mood in self._moods[group]:
                if mood.name == mood_name:
                    return mood