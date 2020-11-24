from typing import List, Union
from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.device import light
from pytradfri.group import Group
from .light import Lights, LightHandler
from .group import Groups, GroupHandler
from .common import try_several_times
from ..config import config

logger = config.logger
gateway = Gateway()
LightsOrGroups = Union[Lights, Groups, List[Union[Lights, Groups]]]


class TradfriGateway:
    _light_handler = LightHandler(gateway)
    _group_handler = GroupHandler(gateway)

    @staticmethod
    def update() -> None:
        TradfriGateway._light_handler.update()
        TradfriGateway._group_handler.update()

    @staticmethod
    def reboot() -> None:
        """Reboot the gateway"""
        try_several_times(gateway.reboot())

    @staticmethod
    def turn_on(light_or_group: LightsOrGroups) -> None:
        # List (iterate)
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.turn_on(i)

        # Light Device
        elif isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    try_several_times(light_device.light_control.set_state(1))

                # Socket
                elif light_device.has_socket_control:
                    try_several_times(light_device.socket_control.set_state(1))

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)
            if group:
                try_several_times(group.set_state(1))

    @staticmethod
    def turn_off(light_or_group: LightsOrGroups) -> None:
        # List (iterate)
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.turn_off(i)

        # Light Device
        elif isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    try_several_times(light_device.light_control.set_state(0))

                # Socket
                elif light_device.has_socket_control:
                    try_several_times(light_device.socket_control.set_state(0))

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)
            if group:
                try_several_times(group.set_state(0))

    @staticmethod
    def isOn(light_or_group: Union[Lights, Groups]) -> bool:
        """Check if a light or group is turned on or not"""
        # Light
        if isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    return bool(light_device.light_control.lights[0].state)

                # Socket
                elif light_device.has_socket_control:
                    return bool(light_device.socket_control.sockets[0].state)

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)
            if group:
                return bool(group.state)

        return False

    @staticmethod
    def toggle(light_or_group: LightsOrGroups, update: bool = True) -> None:
        if update:
            TradfriGateway._light_handler.update()
            TradfriGateway._group_handler.update()

        # List (iterate)
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.toggle(i, update=False)

        # Light
        elif isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    new_state = not bool(light_device.light_control.lights[0].state)
                    try_several_times(light_device.light_control.set_state(new_state))

                # Socket
                elif light_device.has_socket_control:
                    new_state = not bool(light_device.socket_control.sockets[0].state)
                    try_several_times(light_device.socket_control.set_state(new_state))

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)

            if group:
                new_state = not bool(group.state)
                try_several_times(group.set_state(new_state))

    @staticmethod
    def dim(
        light_or_group: LightsOrGroups,
        value: int,
        transition_time: float = 1,
    ) -> None:
        """Dim lights and groups

        Args:
            light_or_group (LightsOrGroups): List of light and groups or a single light or group
            value (int): Dim between 0 and 254
            transition_time (float, optional): In seconds. Defaults to 1.
        """
        # Logging
        if isinstance(light_or_group, Lights) or isinstance(light_or_group, Groups):
            logger.debug(
                f"TradfriGateway.dim() Dim {light_or_group.value} to {value} with transition time {transition_time} seconds."
            )

        transition_time_in_tradfri = TradfriGateway._time_in_tradfri(transition_time)

        # List
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.dim(i, value, transition_time=transition_time)

        # Light Device
        elif isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:
                # Light Bulb
                if (
                    light_device.has_light_control
                    and light_device.light_control.can_set_dimmer
                ):
                    try_several_times(
                        light_device.light_control.set_dimmer(
                            value, transition_time=transition_time_in_tradfri
                        )
                    )

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)
            if group:
                try_several_times(
                    group.set_dimmer(value, transition_time=transition_time_in_tradfri)
                )

    @staticmethod
    def color(
        light_or_group: LightsOrGroups,
        x: int,
        y: int,
        transition_time: float = 1,
    ) -> None:
        """Set the color of a light or group

        Args:
            light_or_group (LightsOrGroups): List of light and groups or a single light or group
            x (int): x-value of the color
            y (int): y-value of the color
            transition_time (float, optional): Time in seconds to transition to the color. Defaults to 1.
        """

        transition_time_in_tradfri = TradfriGateway._time_in_tradfri(transition_time)

        # List (iterate)
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.color(i, x, y, transition_time)

        # Light Device
        elif isinstance(light_or_group, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                light_or_group
            )
            if light_device:
                # Light Bulb
                if (
                    light_device.has_light_control
                    and light_device.light_control.can_set_xy
                ):
                    try_several_times(
                        light_device.light_control.set_xy_color(
                            x, y, transition_time=transition_time_in_tradfri
                        )
                    )

        # Group
        elif isinstance(light_or_group, Groups):
            group = TradfriGateway._group_handler.get_group(light_or_group)
            if group:
                try_several_times(
                    group.set_xy_color(x, y, transition_time=transition_time_in_tradfri)
                )

    @staticmethod
    def mood(groups: LightsOrGroups, mood_name: str) -> None:
        """Set the mood for a group

        Args:
            groups (LightsOrGroups): The groups to set moods for. If a light is specified it is simply ignored
            mood_name (str): Name of the mood to turn on
        """
        if isinstance(groups, list):
            for group in groups:
                TradfriGateway.mood(group, mood_name)

        elif isinstance(groups, Groups):
            group = TradfriGateway._group_handler.get_group(groups)
            mood = TradfriGateway._group_handler.get_mood(groups, mood_name)
            if group and mood:
                try_several_times(group.activate_mood(mood.id))

    @staticmethod
    def _time_in_tradfri(seconds: float) -> int:
        """Convert seconds to measured time in tradfri (100ms)

        Args:
            seconds (float): Number of seconds

        Returns:
            int: Time measured in tradfri
        """
        return int(seconds * 10)
