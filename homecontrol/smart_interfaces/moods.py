from __future__ import annotations

from enum import Enum
from typing import Union

_MAX_COLOR_INT = 65535


class Mood:
    def __init__(
        self,
        name: str,
        brightness: Union[int, float],
        x: Union[int, float],
        y: Union[int, float],
    ) -> None:
        self.name = name
        self.brightness = brightness

        # X color
        if isinstance(x, int):
            self.x = x
        else:
            self.x = int(x * _MAX_COLOR_INT)

        # Y color
        if isinstance(y, int):
            self.y = y
        else:
            self.y = int(y * _MAX_COLOR_INT)


class Moods(Enum):
    sunset = Mood("Sunset", 1, 0.68, 0.32)

    @staticmethod
    def from_name(name: str) -> Union[Moods, None]:
        name = name.lower()
        for mood in Moods:
            if mood.value.name.lower() == name:
                return mood