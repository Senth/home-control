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
        x_start = 46000
        x_stop = 32908
        y_start = 19650
        y_stop = 29591

        # Set starting brightness to 1 and color to red
        self.add_transition(BrightnessTransition(brightness_start, 0))
        self.add_transition(ColorTransition(x_start, y_start, 0))

        # Transition to yellow and 70 in brightness over 10 minutes
        transitions = BrightnessColorTransitionFactory.create(
            brightness_start, brightness_stop, x_start, x_stop, y_start, y_stop, 600
        )
        self.add_transitions(transitions)

        # Transition to bright white over 10 minutes
        brightness_start = 70
        brightness_stop = 254
        x_start = 32908
        x_stop = 21150
        y_start = 29591
        y_stop = 21150

        transitions = BrightnessColorTransitionFactory.create(
            brightness_start, brightness_stop, x_start, x_stop, y_start, y_stop, 600
        )
        self.add_transitions(transitions)
