from ..tradfri_gateway import TradfriGateway
from ...config import config

_logger = config.logger


class Transition:
    """Base transition with the transition time
    :param transition_time number of seconds to transition
    """

    def __init__(self, transition_time):
        self.transition_time = transition_time

    def run(self, light_or_group):
        _logger.debug(
            "Transition.run() Nothing running, transition_time {} seconds ".format(
                self.transition_time
            )
        )


class ColorTransition(Transition):
    def __init__(self, x, y, transition_time):
        super().__init__(transition_time)
        self.x = x
        self.y = y

    def run(self, light_or_group):
        _logger.debug(
            "ColorTransition.run() Transitioning to ({}, {}) in {}".format(
                self.x, self.y, self.transition_time
            )
        )
        TradfriGateway.color(
            light_or_group, self.x, self.y, transition_time=self.transition_time
        )


class BrightnessTransition(Transition):
    """Transition the time
    :param light_or_group: Can be either a light or group. Can be a list of lights and groups
    :param brightness the dim value between 0 and 254
    :param transition_time time in seconds (can be float)
    """

    def __init__(self, brightness, transition_time):
        super().__init__(transition_time)
        self.brightness = brightness

    def run(self, light_or_group):
        _logger.debug(
            "BrightnessTransition.run() Transitioning to light level {} in {} seconds".format(
                self.brightness, self.transition_time
            )
        )
        TradfriGateway.dim(light_or_group, self.brightness, self.transition_time)


class BrightnessColorTransitionFactory:
    TRANSITION_TIME_PART = 10

    @staticmethod
    def create(
        brightness_from,
        brightness_to,
        color_x_from,
        color_x_to,
        color_y_from,
        color_y_to,
        transition_time,
    ):

        part_count = (
            transition_time / BrightnessColorTransitionFactory.TRANSITION_TIME_PART / 2
        )
        brightness_parts = BrightnessColorTransitionFactory._calculate_parts(
            brightness_from, brightness_to, part_count
        )
        color_x_parts = BrightnessColorTransitionFactory._calculate_parts(
            color_x_from, color_x_to, part_count
        )
        color_y_parts = BrightnessColorTransitionFactory._calculate_parts(
            color_y_from, color_y_to, part_count
        )

        part_count = len(brightness_parts)

        transitions = []

        # Create initial position
        transitions.append(BrightnessTransition(brightness_from, 0))
        transitions.append(ColorTransition(color_x_from, color_y_from, 0))

        # Alternate creating transitions between color and brightness
        for i in range(part_count):
            # Wait transition
            transitions.append(Transition(0.5))

            # Color transition
            x = color_x_parts[i]
            y = color_y_parts[i]
            transitions.append(
                ColorTransition(
                    x, y, BrightnessColorTransitionFactory.TRANSITION_TIME_PART
                )
            )

            # Wait transition
            transitions.append(Transition(0.5))

            # Brightness transition
            brightness = brightness_parts[i]
            transitions.append(
                BrightnessTransition(
                    brightness, BrightnessColorTransitionFactory.TRANSITION_TIME_PART
                )
            )

        return transitions

    @staticmethod
    def _calculate_parts(fro, to, part_count):
        diff_value = to - fro
        part_increment = diff_value / part_count
        i = 1
        parts_list = []

        while i < part_count:
            value = fro + part_increment * i
            parts_list.append(int(value))
            i += 1

        # Add the last part to the end (i.e. the variable 'to')
        parts_list.append(to)

        return parts_list

    def create_transition(self):
        pass
