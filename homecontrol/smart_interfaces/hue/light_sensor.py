from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict

from tealprint import TealPrint

from ...data.stats import Stats
from .sensor import Sensor


class _Range:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max


class LightLevels(Enum):
    fully_dark = 0
    dark = 1
    partially_dark = 2
    partially_light = 3
    light = 4
    unknown = 5


class LightSensor(Sensor):
    _update_interval = 60 * 5
    _threshold = 500

    def __init__(
        self, id: int, name: str, dark: int, partially_dark: int, partially_light: int, light: int, log: bool = False
    ) -> None:
        super().__init__(id, name, LightSensor._update_interval, log)
        self.light_level: int = 0
        self.level_name = LightLevels.light
        self.ranges = {
            LightLevels.fully_dark: _Range(0, dark),
            LightLevels.dark: _Range(dark, partially_dark),
            LightLevels.partially_dark: _Range(partially_dark, partially_light),
            LightLevels.partially_light: _Range(partially_light, light),
            LightLevels.light: _Range(light, 999999),
            LightLevels.unknown: _Range(-999, -999),
        }

    def is_level_or_below(self, level: LightLevels) -> bool:
        return self.level_name.value <= level.value

    def is_level_or_above(self, level: LightLevels) -> bool:
        return self.level_name.value >= level.value

    def on_update(self, data: Dict[str, Any]) -> None:
        self.light_level = data["state"]["lightlevel"]
        self.update_light_level()

        if self.log:
            info = {
                "name": self.name,
                "level_name": self.level_name.name,
                "level_value": self.light_level,
            }
            Stats.log("light_level", json.dumps(info))

            TealPrint.verbose(f"☀ {self.name}: {self.light_level} lux, range: {self.level_name.name}")

    def get_light_name_from_level(self) -> LightLevels:
        for light_level in LightLevels:
            range = self._get_range(light_level)
            if range.min <= self.light_level and self.light_level <= range.max:
                return light_level
        return LightLevels.unknown

    def update_light_level(self) -> None:
        new_level_name = self.get_light_name_from_level()

        # Skip if level wasn't changed
        if new_level_name == self.level_name:
            return

        # Check threshold
        if self._is_within_threshold(self.light_level):
            return

        self.level_name = new_level_name

    def _is_within_threshold(self, value: int) -> bool:
        return self._range.min - LightSensor._threshold <= value and value <= self._range.max + LightSensor._threshold

    def _get_range(self, level: LightLevels) -> _Range:
        return self.ranges[level]

    @property
    def _range(self) -> _Range:
        return self.ranges[self.level_name]
