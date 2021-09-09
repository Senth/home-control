from time import sleep
from typing import List

from tealprint import TealPrint

from ..interface import Interface
from .transitions import Transition


class Effect:
    def __init__(self, interfaces: List[Interface], name: str) -> None:
        self.name = name
        self.interfaces = interfaces
        self.transitions: List[Transition] = []
        self.running = False
        self.reset()

    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def add_transitions(self, transitions: List[Transition]) -> None:
        for transition in transitions:
            self.add_transition(transition)

    def reset(self) -> None:
        self.aborted = False

    def abort(self) -> None:
        self.aborted = True

    def run(self) -> None:
        if not self.running:
            self.running = True

            TealPrint.debug("Effect.run() " + self.name)
            for transition in self.transitions:
                if self.aborted:
                    self.running = False
                    break

                transition.run(self.interfaces)
                transition_time = transition.transition_time

                if transition_time and transition_time > 0:
                    sleep(transition_time)

            self.running = False

        self.reset()
