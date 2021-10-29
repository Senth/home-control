from __future__ import annotations

from enum import Enum
from typing import Union

from ..core.entities.color import Color


class Mood:
    def __init__(self, name: str, brightness: Union[int, float], color: Color) -> None:
        self.name = name
        self.brightness = brightness
        self.color = color


class Moods(Enum):
    sunset = Mood("Sunset", 1, Color.from_xy(0.68, 0.32))

    @staticmethod
    def from_name(name: str) -> Union[Moods, None]:
        name = name.lower()
        for mood in Moods:
            if mood.value.name.lower() == name:
                return mood
