from typing import List, Union
from threading import Thread
from pytradfri import Gateway
from pytradfri.device import Device
from . import LightsAndGroups
from .light import Lights, LightHandler
from .group import Groups, GroupHandler
from .motion_sensor import MotionSensor
from .common import try_several_times
from ..config import config

_logger = config.logger
_gateway = Gateway()
MotionSensor.set_gateway(_gateway)


class TradfriGateway:
    _light_handler = LightHandler(_gateway)
    _group_handler = GroupHandler(_gateway)
    _devices: List[Device] = []

    @staticmethod
    def update() -> None:
        TradfriGateway._devices = TradfriGateway._get_devices()
        TradfriGateway._light_handler.update(TradfriGateway._get_light_devices())
        TradfriGateway._group_handler.update()

    @staticmethod
    def _get_devices() -> List[Device]:
        devices: List[Device] = []
        devices = try_several_times(_gateway.get_devices(), execute_response=True)
        return devices

    @staticmethod
    def _get_light_devices() -> List[Device]:
        lights: List[Device] = []

        for device in TradfriGateway._devices:
            if device.has_light_control or device.has_socket_control:
                lights.append(device)

        return lights

    @staticmethod
    def reboot() -> None:
        """Reboot the gateway"""
        try_several_times(_gateway.reboot())

    @staticmethod
    def turn_on(lights_and_groups: LightsAndGroups) -> None:
        # List (iterate)
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.turn_on(i)

        # Light Device
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    try_several_times(light_device.light_control.set_state(1))

                # Socket
                elif light_device.has_socket_control:
                    try_several_times(light_device.socket_control.set_state(1))

        # Group
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                try_several_times(group.set_state(1))

    @staticmethod
    def turn_off(lights_and_groups: LightsAndGroups) -> None:
        # List (iterate)
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.turn_off(i)

        # Light Device
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    try_several_times(light_device.light_control.set_state(0))

                # Socket
                elif light_device.has_socket_control:
                    try_several_times(light_device.socket_control.set_state(0))

        # Group
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                try_several_times(group.set_state(0))

    @staticmethod
    def isOn(lights_and_groups: Union[Lights, Groups]) -> bool:
        """Check if a light or group is turned on or not"""
        # Light
        if isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
            )
            if light_device:

                # Light Bulb
                if light_device.has_light_control:
                    return bool(light_device.light_control.lights[0].state)

                # Socket
                elif light_device.has_socket_control:
                    return bool(light_device.socket_control.sockets[0].state)

        # Group
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                return bool(group.state)

        return False

    @staticmethod
    def toggle(lights_and_groups: LightsAndGroups, update: bool = True) -> None:
        if update:
            TradfriGateway._light_handler.update(TradfriGateway._get_light_devices())
            TradfriGateway._group_handler.update()

        # List (iterate)
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.toggle(i, update=False)

        # Light
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
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
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)

            if group:
                new_state = not bool(group.state)
                try_several_times(group.set_state(new_state))

    @staticmethod
    def dim(
        lights_and_groups: LightsAndGroups,
        value: Union[float, int],
        transition_time: float = 1,
    ) -> None:
        """Dim lights and groups

        Args:
            lights_and_groups (LightsAndGroups): List of light and groups or a single light or group.
            value (float,int): Dim between 0.0 and 1.0 (0.0 turns off the light), or 0 and 254.
            transition_time (float, optional): In seconds. Defaults to 1.0
        """
        # Normalize to 0-254
        if isinstance(value, float):
            tradfriValue = round(value * 254)
        else:
            tradfriValue = max(0, min(254, value))

        # Logging
        if isinstance(lights_and_groups, Lights) or isinstance(
            lights_and_groups, Groups
        ):
            _logger.debug(
                f"TradfriGateway.dim() Dim {lights_and_groups.value} to {tradfriValue} ({value}) with transition time {transition_time} seconds."
            )

        transition_time_in_tradfri = TradfriGateway._time_in_tradfri(transition_time)

        # List
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.dim(i, value, transition_time=transition_time)

        # Light Device
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
            )
            if light_device:
                # Light Bulb
                if (
                    light_device.has_light_control
                    and light_device.light_control.can_set_dimmer
                ):
                    try_several_times(
                        light_device.light_control.set_dimmer(
                            tradfriValue, transition_time=transition_time_in_tradfri
                        )
                    )

        # Group
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                try_several_times(
                    group.set_dimmer(
                        tradfriValue, transition_time=transition_time_in_tradfri
                    )
                )

    @staticmethod
    def color_xy(
        lights_and_groups: LightsAndGroups,
        x: int,
        y: int,
        transition_time: float = 1,
    ) -> None:
        """Set the color of a light or group

        Args:
            lights_and_groups (LightsAndGroups): List of light and groups or a single light or group
            x (int): x-value of the color
            y (int): y-value of the color
            transition_time (float, optional): Time in seconds to transition to the color. Defaults to 1.
        """

        transition_time_in_tradfri = TradfriGateway._time_in_tradfri(transition_time)

        # List (iterate)
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.color_xy(i, x, y, transition_time)

        # Light Device
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
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
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                try_several_times(
                    group.set_xy_color(x, y, transition_time=transition_time_in_tradfri)
                )

    @staticmethod
    def color_hex(
        lights_and_groups: LightsAndGroups,
        hex_color: str,
        transition_time: float = 1,
    ) -> None:
        """Set the color of a light or group

        Args:
            lights_and_groups (LightsAndGroups): List of light and groups or a single light or group
            hex_color (str): color in hex format #ffffff
            transition_time (float, optional): Time in seconds to transition to the color. Defaults to 1.
        """

        transition_time_in_tradfri = TradfriGateway._time_in_tradfri(transition_time)

        # List (iterate)
        if isinstance(lights_and_groups, list):
            for i in lights_and_groups:
                TradfriGateway.color_hex(i, hex_color, transition_time)

        # Light Device
        elif isinstance(lights_and_groups, Lights):
            light_device = TradfriGateway._light_handler.get_light_device(
                lights_and_groups
            )
            if light_device:
                # Light Bulb
                if (
                    light_device.has_light_control
                    and light_device.light_control.can_set_color
                ):
                    try_several_times(
                        light_device.light_control.set_hex_color(
                            hex_color, transition_time=transition_time_in_tradfri
                        )
                    )

        # Group
        elif isinstance(lights_and_groups, Groups):
            group = TradfriGateway._group_handler.get_group(lights_and_groups)
            if group:
                try_several_times(
                    group.set_hex_color(
                        hex_color, transition_time=transition_time_in_tradfri
                    )
                )

    @staticmethod
    def _time_in_tradfri(seconds: float) -> int:
        """Convert seconds to measured time in tradfri (100ms)

        Args:
            seconds (float): Number of seconds

        Returns:
            int: Time measured in tradfri
        """
        return int(seconds * 10)
