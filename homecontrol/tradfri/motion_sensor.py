from pytradfri.group import Group
from typing import List, Union
from pytradfri.gateway import Gateway
from .common import try_several_times
from enum import Enum
from ..config import config


_logger = config.logger


class MotionSensor:
    _gateway: Gateway
    _groups: List[Group]

    def __init__(self, name: str) -> None:
        self.on = False
        self.name = name
        self.id = 0
        self._group: Union[Group, None] = None

    def update(self) -> None:
        if self._group:
            # _logger.info(f"Updating motion sensor {self.name}")
            [group] = try_several_times(MotionSensor._gateway.get_group(self.id))
            if isinstance(group, Group):
                _logger.info(f"{group.raw}")
                self._group = group
        # Set device from gotten devices
        else:
            for group in MotionSensor._groups:
                if group.name == self.name:
                    self._group = group
                    self.id = group.id
                    _logger.info(f"Found motion sensor {group.name} with id {group.id}")
                    _logger.info(
                        f"State: {group.state}\nDimmer: {group.dimmer}\nRaw: {group.raw}"
                    )
                    # try_several_times(group.set_state(False))

    def _set_state(self, on) -> None:
        prev_state = self.on
        self.on = on

        if prev_state != self.on:
            was = "On" if prev_state else "Off"
            now = "On" if self.on else "Off"
            _logger.info(f"Motion sensor changed {was} -> {now}")

    @staticmethod
    def update_all() -> None:
        devices: Union[None, List[Group]]

        for sensor_enum in MotionSensors:
            sensor = sensor_enum.value
            sensor.update()

    @staticmethod
    def set_gateway(gateway: Gateway) -> None:
        MotionSensor._gateway = gateway
        MotionSensor._groups = try_several_times(
            MotionSensor._gateway.get_groups(), execute_response=True
        )


class MotionSensors(Enum):
    hall = MotionSensor("Hall Motion Sensor Group")