from __future__ import annotations

from enum import Enum
from typing import Union

from .sunrise_bamboo import SunriseBamboo
from .test_effect import TestEffect


class Effects(Enum):
    bamboo_sunrise = SunriseBamboo()
    test = TestEffect()

    @staticmethod
    def from_name(name: str) -> Union[Effects, None]:
        name = name.lower()
        for effect in Effects:
            if effect.value.name.lower() == name:
                return effect
