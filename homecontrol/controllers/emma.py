from enum import Enum
from typing import List

from ..data.network import GuestOf, Network
from ..smart_interfaces.groups import Groups
from .controller import Controller, States


class ControlTurnOffEmma(Controller):
    def __init__(self):
        super().__init__("Turn off Emma lights")

    def _get_interfaces(self) -> List[Enum]:
        return [Groups.emma]

    def update(self):
        # Turn off if Emma isn't home and there's no guest
        if Network.mobile_emma.is_on() or Network.is_guest_home(GuestOf.both, GuestOf.emma):
            self.state = States.on

    def turn_on(self):
        pass
