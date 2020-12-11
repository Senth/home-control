from __future__ import annotations
from enum import Enum
from typing import Union
from .sunrise_bamboo import SunriseBamboo
from .test_effect import TestEffect
from .effect import Effect


class Effects(Enum):
    bamboo_sunrise = SunriseBamboo()
    test = TestEffect()

    @staticmethod
    def from_name(name: str) -> Union[Effect, None]:
        for effect in Effects:
            if effect.value.name.lower() == name.lower():
                return effect.value
