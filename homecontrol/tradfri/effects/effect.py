from time import sleep
from .transitions import Transition
from .. import LightsAndGroups
from ...config import config

_logger = config.logger


class Effect:
    def __init__(self, light_or_group: LightsAndGroups, name: str) -> None:
        self.name = name
        self.light_or_group = light_or_group
        self.transitions = []
        self.running = False
        self.reset()

    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def add_transitions(self, transitions: list) -> None:
        for transition in transitions:
            self.add_transition(transition)

    def reset(self) -> None:
        self.aborted = False

    def abort(self) -> None:
        self.aborted = True

    def run(self) -> None:
        if not self.running:
            self.running = True

            _logger.debug("Effect.run() " + self.name)
            for transition in self.transitions:
                if self.aborted:
                    self.running = False
                    break

                transition.run(self.light_or_group)
                transition_time = transition.transition_time

                if transition_time and transition_time > 0:
                    sleep(transition_time)

            self.running = False

        self.reset()