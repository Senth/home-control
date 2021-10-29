from ...core.entities.color import Color
from ..devices import Devices
from .effect import Effect
from .transitions import (
    BrightnessColorTransitionFactory,
    BrightnessTransition,
    ColorTransition,
)


class SunriseBamboo(Effect):
    def __init__(self) -> None:
        super().__init__([Devices.bamboo.value], "Sunrise Bamboo")

        brightness_start = 1
        brightness_stop = 70
        color_start = Color.from_xy(0.7019, 0.2998)
        color_end = Color.from_xy(0.5021, 0.4515)

        # Set starting brightness to 1 and color to red
        self.add_transition(BrightnessTransition(brightness_start, 0))
        self.add_transition(ColorTransition(color_start, 0))

        # Transition to yellow and 70 in brightness over 10 minutes
        transitions = BrightnessColorTransitionFactory.create(
            brightness_start, brightness_stop, color_start, color_end, 600
        )
        self.add_transitions(transitions)

        # Transition to bright white over 10 minutes
        brightness_start = 70
        brightness_stop = 254
        color_start = color_end
        color_end = Color.from_xy(0.3227, 0.3227)

        transitions = BrightnessColorTransitionFactory.create(
            brightness_start, brightness_stop, color_start, color_end, 600
        )
        self.add_transitions(transitions)
