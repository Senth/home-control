from typing import Union


class Interface:
    """An interface for lights, groups, etc"""

    def __init__(self, name: str) -> None:
        self.name = name

    def turn_on(self) -> None:
        raise NotImplementedError()

    def turn_off(self) -> None:
        raise NotImplementedError()

    def toggle(self) -> None:
        raise NotImplementedError()

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        """Dim lights and groups

        Args:
            value (Union[float, int]): Dim between 0.0 and 1.0 (0.0 turns off the lights), or 0 and 254.
            transition_time (float, optional): In seconds. Defaults to 1.
        """
        raise NotImplementedError()

    def update(self) -> None:
        raise NotImplementedError()

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        """Set the color of the light or group

        Args:
            transition_time (float, optional): In seconds. Defaults to 1.
        """
        raise NotImplementedError()