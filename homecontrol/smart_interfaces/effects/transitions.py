from typing import List, Union

from tealprint import TealPrint

from ...core.entities.color import Color
from ..interface import Interface


class Transition:
    """Base transition with the transition time
    :param transition_time number of seconds to transition
    """

    def __init__(self, transition_time: float):
        self.transition_time = transition_time

    def run(self, interfaces: List[Interface]):
        TealPrint.debug(f"Transition.run() Nothing running, transition_time {self.transition_time} seconds ")


class ColorTransition(Transition):
    def __init__(self, color: Color, transition_time: float):
        super().__init__(transition_time)
        self.color = color

    def run(self, interfaces: List[Interface]):
        TealPrint.debug(f"ColorTransition.run() Transitioning to ({self.color}) in {self.transition_time}")
        for interface in interfaces:
            interface.color(self.color, self.transition_time)


class BrightnessTransition(Transition):
    """Transition the time
    :param light_or_group: Can be either a light or group. Can be a list of lights and groups
    :param brightness the dim value between 0 and 254
    :param transition_time time in seconds (can be float)
    """

    def __init__(self, brightness: Union[int, float], transition_time: float):
        super().__init__(transition_time)
        self.brightness = brightness

    def run(self, interfaces: List[Interface]):
        TealPrint.debug(
            "BrightnessTransition.run() Transitioning to light level {} in {} seconds".format(
                self.brightness, self.transition_time
            )
        )
        for interface in interfaces:
            interface.dim(self.brightness, self.transition_time)


class BrightnessColorTransitionFactory:
    TRANSITION_TIME_PART = 10

    @staticmethod
    def create(
        brightness_from: Union[int, float],
        brightness_to: Union[int, float],
        color_start: Color,
        color_end: Color,
        transition_time,
    ):

        part_count = transition_time / BrightnessColorTransitionFactory.TRANSITION_TIME_PART / 2
        brightness_parts = BrightnessColorTransitionFactory._calculate_individual_parts(
            brightness_from, brightness_to, part_count
        )
        color_parts = BrightnessColorTransitionFactory._calculate_parts(color_start, color_end, part_count)

        part_count = len(brightness_parts)

        transitions = []

        # Create initial position
        transitions.append(BrightnessTransition(brightness_from, 0))
        transitions.append(ColorTransition(color_start, 0))

        # Alternate creating transitions between color and brightness
        for i in range(part_count):
            # Wait transition
            transitions.append(Transition(0.5))

            # Color transition
            color = color_parts[i]
            transitions.append(ColorTransition(color, BrightnessColorTransitionFactory.TRANSITION_TIME_PART))

            # Wait transition
            transitions.append(Transition(0.5))

            # Brightness transition
            brightness = brightness_parts[i]
            transitions.append(BrightnessTransition(brightness, BrightnessColorTransitionFactory.TRANSITION_TIME_PART))

        return transitions

    @staticmethod
    def _calculate_parts(fro: Color, to: Color, part_count: int) -> List[Color]:
        parts = []
        if fro.x and fro.y and to.x and to.y:
            x_parts = BrightnessColorTransitionFactory._calculate_individual_parts(fro.x, to.x, part_count)
            y_parts = BrightnessColorTransitionFactory._calculate_individual_parts(fro.y, to.y, part_count)

            for i in range(part_count):
                x = x_parts[i]
                y = y_parts[i]
                parts.append(Color.from_xy(x, y))

        return parts

    @staticmethod
    def _calculate_individual_parts(
        fro: Union[float, int], to: Union[float, int], part_count: int
    ) -> List[Union[float, int]]:
        diff_value = to - fro
        part_increment = diff_value / part_count
        i = 1
        parts_list = []

        while i < part_count:
            value = fro + part_increment * i
            if isinstance(fro, int):
                value = int(value)
            parts_list.append(value)
            i += 1

        # Add the last part to the end (i.e. the variable 'to')
        parts_list.append(to)

        return parts_list

    def create_transition(self):
        pass
