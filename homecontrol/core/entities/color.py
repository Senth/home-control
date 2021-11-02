from __future__ import annotations

from typing import Optional, Union

_MAX_COLOR_INT = 65535


class Color:
    """Common package for setting the color"""

    def __init__(self) -> None:
        self.x: Optional[float] = None
        self.y: Optional[float] = None
        self.saturation: Optional[int] = None
        self.hue: Optional[int] = None
        self.temperature: Optional[int] = None

    def __members(self):
        return [
            self.x,
            self.y,
            self.saturation,
            self.hue,
            self.temperature,
        ]

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self) -> int:
        return hash(self.__members())

    def __repr__(self) -> str:
        return str(self.__members())

    def __str__(self) -> str:
        return str(self.__members())

    @staticmethod
    def from_xy(x: float, y: float) -> Color:
        color = Color()
        color.x = x
        color.y = y
        return color

    @staticmethod
    def from_hue(hue: Union[int, float]) -> Color:
        """
        The hue value to set light to.
        The hue value is a wrapping value between 0 and 65535.
        Both 0 and 65535 are red, 25500 is green and 46920 is blue.
        When using a float the value 1.0 == 65535
        """
        color = Color()

        if isinstance(hue, int):
            color.hue = hue
        elif isinstance(hue, float):
            color.hue = int(hue * _MAX_COLOR_INT)

        return color

    @staticmethod
    def from_saturation(saturation: Union[int, float]) -> Color:
        """
        Saturation of the light.
        254 is the most saturated (colored) and 0 is the least saturated (white).
        When using a float the value 1.0 == 254
        """
        color = Color()

        if isinstance(saturation, int):
            color.saturation = saturation
        elif isinstance(saturation, float):
            color.saturation = int(saturation * 254)

        return color

    @staticmethod
    def from_temperature(temperature: Union[int, float]) -> Color:
        """
        The Mired color temperature of the light.
        Available from 2000K -> 6500K
        When using float 0.0 == 2000K and 1.0 == 6500K
        2012 connected lights are capable of 153 (6500K) to 500 (2000K).
        """
        color = Color()

        if isinstance(temperature, int):
            color.temperature = temperature
        elif isinstance(temperature, float):
            color.temperature = int(temperature * 4500) + 2000

        # Normalize and invert
        # 153 == 6500K and 500 == 2000K
        color.temperature = int(color.temperature / (500 - 153)) + 153
        color.temperature = 500 - color.temperature

        return color
