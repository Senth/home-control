from typing import Union

from ..core.entities.color import Color
from .moods import Mood


class Interface:
    """An interface for lights, groups, etc"""

    def __init__(self, name: str) -> None:
        self.name = name

    def turn_on(self) -> None:
        pass

    def turn_off(self) -> None:
        pass

    def toggle(self) -> None:
        pass

    def is_on(self) -> None:
        pass

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        """Dim lights and groups

        Args:
            value (Union[float, int]): Dim between 0.0 and 1.0 (0.0 turns off the lights), or 0 and 254.
            transition_time (float, optional): In seconds. Defaults to 1.
        """
        pass

    @staticmethod
    def normalize_dim(value: Union[float, int]) -> int:
        """Normalize dim value to be between 0 and 254"""
        if isinstance(value, float):
            value = round(value * 254)
        normalized = max(0, min(254, value))
        return normalized

    @staticmethod
    def normalize_transition_time(seconds: float) -> int:
        return int(seconds * 10)

    def update(self) -> None:
        pass

    def color(self, color: Color, transition_time: float = 1) -> None:
        """Set the color of the light or group

        Args:
            transition_time (float, optional): In seconds. Defaults to 1.
        """
        pass

    def mood(self, mood: Mood) -> None:
        """Set the mood for an interface if applicable"""
