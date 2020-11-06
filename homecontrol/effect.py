from time import sleep
from .tradfri_gateway import TradfriGateway, Lights

import logging

logger = logging.getLogger(__name__)


class Effects:
    @staticmethod
    def sunrise_bamboo():
        effect = Effect(Lights.bamboo, "Sunrise Bamboo")

        brightness_start = 1
        brightness_stop = 70
        x_start = 46000
        x_stop = 32908
        y_start = 19650
        y_stop = 29591

        # Set starting brightness to 1 and color to red
        effect.add_transition(BrightnessTransition(brightness_start, 0))
        effect.add_transition(ColorTransition(x_start, y_start, 0))

        # Transition to yellow and 70 in brightness over 10 minutes
        transitions = BrightnessColorTransitionFactory.create(
            brightness_start, brightness_stop, x_start, x_stop, y_start, y_stop, 600
        )
        effect.add_transitions(transitions)

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
        effect.add_transitions(transitions)

        return effect

    @staticmethod
    def test_effect():
        effect = Effect(Lights.bamboo, "Test Bamboo")

        # effect.add_transition(BrightnessTransition(1, 0))
        # effect.add_transition(BrightnessTransition(250, 5))
        # effect.add_transition(BrightnessTransition(1, 5))

        # effect.add_transition(ColorTransition(46000, 19650, 0))
        # effect.add_transition(ColorTransition(21150, 21150, 10))
        # effect.add_transitions(BrightnessColorTransitionFactory.create(
        #     1, 254,
        #     46000, 21150,
        #     19650, 21150,
        #     30
        # ))

        # brightness_start = 1
        # brightness_stop = 70
        # x_start = 46000
        # x_stop = 32908
        # y_start = 19650
        # y_stop = 29591

        # # Set starting brightness to 1 and color to red
        # effect.add_transition(BrightnessTransition(brightness_start, 0))
        # effect.add_transition(ColorTransition(x_start, y_start, 0))

        # # Transition to yellow and 70 in brightness over 10 minutes
        # transitions = BrightnessColorTransitionFactory.create(
        #     brightness_start, brightness_stop,
        #     x_start, x_stop,
        #     y_start, y_stop,
        #     60
        # )
        # effect.add_transitions(transitions)

        # # Transition to bright white over 10 minutes
        # brightness_start = 70
        # brightness_stop = 254
        # x_start = 32908
        # x_stop = 21150
        # y_start = 29591
        # y_stop = 21150

        # transitions = BrightnessColorTransitionFactory.create(
        #     brightness_start, brightness_stop,
        #     x_start, x_stop,
        #     y_start, y_stop,
        #     60
        # )
        # effect.add_transitions(transitions)

        return effect

    @staticmethod
    def from_name(name):
        if name == "sunrise_bamboo":
            return Effects.sunrise_bamboo()
        elif name == "test_effect":
            return Effects.test_effect()
        else:
            logger.warning("Effects.from_name() No effect named " + name)


class Transition:
    """Base transition with the transition time
    :param transition_time number of seconds to transition
    """

    def __init__(self, transition_time):
        self.transition_time = transition_time

    def run(self, light_or_group):
        logger.debug(
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
        logger.debug(
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
        logger.debug(
            "BrightnessTransition.run() Transitioning to light level {} in {} seconds".format(
                self.brightness, self.transition_time
            )
        )
        TradfriGateway.dim(light_or_group, self.brightness, self.transition_time)


class Effect:
    def __init__(self, light_or_group, name):
        self.name = name
        self.light_or_group = light_or_group
        self.transitions = []
        self.abort = False

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def add_transitions(self, transitions: list):
        for transition in transitions:
            self.add_transition(transition)

    def abort(self):
        self.abort = True

    def run(self):
        logger.debug("Effect.run() " + self.name)
        for transition in self.transitions:
            if self.abort:
                return

            transition.run(self.light_or_group)
            transition_time = transition.transition_time

            if transition_time and transition_time > 0:
                sleep(transition_time)


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
