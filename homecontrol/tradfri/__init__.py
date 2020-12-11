from typing import List, Union
from .light import Lights
from .group import Groups
from ..config import config

LightsAndGroups = Union[Lights, Groups, List[Union[Lights, Groups]]]
LightOrGroup = Union[Lights, Groups]


def get_light_and_groups(names: Union[List[str], str]) -> LightsAndGroups:
    """Return all lights and groups with the specified name

    Args:
        name (Union[List[str], str]): Name of the lights and groups to get. If a name isn't found it
        a warning will be logged, but the method will continue without running without that name.

    Returns:
        LightsOrGroups: all found lights and groups that has the specified name(s).
    """
    lightsAndGroups: LightsAndGroups = []

    # Single name
    if isinstance(names, str):
        found = _get_light_or_group(names)
        if found:
            lightsAndGroups.append(found)
    # List of names
    else:
        for name in names:
            found = _get_light_or_group(name)
            if found:
                lightsAndGroups.append(found)

    return lightsAndGroups


def _get_light_or_group(name: str) -> Union[LightOrGroup, None]:
    # Remove 'the ' from the name as IFTTT adds it
    fixed_name = name.lower().replace("the", "").strip()

    light = Lights.from_name(fixed_name)
    if light:
        return light

    group = Groups.from_name(fixed_name)
    if group:
        return group

    config.logger.warning(
        f"get_light_and_groups() Didn't find a light or group with name {name}."
    )
