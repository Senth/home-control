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

    def is_within_threshold(self, value: int) -> bool:
        return self.min - LightSensor._threshold <= value and value <= self.max + LightSensor._threshold


class LightLevels(Enum):
    fully_dark = _Range(0, 6000)
    dark = _Range(6000, 11000)
    partially_dark = _Range(11000, 13500)
    partially_light = _Range(13500, 16000)
    light = _Range(16000, 999999)
    unknown = _Range(-1, -1)

    @staticmethod
    def from_level(level: int) -> LightLevels:
        for light_level in LightLevels:
            if light_level.value.min <= level and level <= light_level.value.max:
                return light_level
        return LightLevels.unknown


class LightSensor(Sensor):
    _update_interval = 60 * 5
    _threshold = 500

    def __init__(self, id: int, name: str, log: bool = False) -> None:
        super().__init__(id, name, LightSensor._update_interval, log)
        self.light_level: int = 0
        self.level_name = LightLevels.light

    def is_level_or_below(self, level: LightLevels) -> bool:
        return self.level_name.value.min <= level.value.min

    def is_level_or_above(self, level: LightLevels) -> bool:
        return self.level_name.value.min >= level.value.min

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

    def update_light_level(self) -> None:
        new_level = LightLevels.from_level(self.light_level)

        # Skip if level wasn't changed
        if new_level == self.level_name:
            return

        # Check threshold
        if self.level_name.value.is_within_threshold(self.light_level):
            return

        self.level_name = new_level
