from time import sleep
from .tradfri_gateway import TradfriGateway

import logging

logger = logging.getLogger(__name__)


class Effect:
    def __init__(self, light_or_group, name):
        self.name = name
        self.light_or_group = light_or_group
        self.transitions = []
        self.abort = False

    def add_transition(self, transition):
        self.transitions.append(transition)

    def add_transitions(self, transitions):
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


class BrightnessColorTransitionFactory:
    TRANSITION_TIME_PART = 100.0

    @staticmethod
    def create(brightness_from, brightness_to, color_x_from, color_y_from, color_x_to, color_y_to, transition_time):

        part_count = transition_time / BrightnessColorTransitionFactory.TRANSITION_TIME_PART
        brightness_parts = BrightnessColorTransitionFactory._calculate_parts(brightness_from, brightness_to, part_count)
        color_x_parts = BrightnessColorTransitionFactory._calculate_parts(color_x_from, color_x_to, part_count)
        color_y_parts = BrightnessColorTransitionFactory._calculate_parts(color_y_from, color_y_to, part_count)

        part_count = len(brightness_parts)

        transitions = []

        # Alternate creating transitions between color and brightness
        for i in range(part_count):
            # Color transition
            x = color_x_parts[i]
            y = color_y_parts[i]
            transitions.append(ColorTransition(x, y, BrightnessColorTransitionFactory.TRANSITION_TIME_PART))

            # Brightness transition
            brightness = brightness_parts[i]
            transitions.append(BrightnessTransition(brightness, BrightnessColorTransitionFactory.TRANSITION_TIME_PART))

        return transitions

    @staticmethod
    def _calculate_parts(fro, to, part_count):
        diff_value = to - fro
        part_increment = diff_value / part_count
        i = 1
        parts_list = []

        while i < part_count:
            value = fro + part_increment * i
            parts_list.append(value)
            i += 1

        # Add the last part to the end (i.e. the variable 'to')
        parts_list.append(to)

        return parts_list

    def create_transition(self):
        pass


class ColorTransition:
    def __init__(self, x, y, transition_time):
        self.x = x
        self.y = y
        self.transititon_time = transition_time

    def run(self, light_or_group):
        TradfriGateway.color(light_or_group, self.x, self.y, transition_time=self.transititon_time)
        sleep(self.transititon_time / 10)


class BrightnessTransition:
    def __init__(self, brightness, transition_time):
        self.brightness = brightness
        self.transition_time = transition_time

    def run(self, light_or_group):
        TradfriGateway.dim(light_or_group, self.brightness, self.transition_time)
        sleep(self.transition_time / 10)


class WaitTransition:
    pass
