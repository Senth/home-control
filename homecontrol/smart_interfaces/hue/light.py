from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Union

from ...core.entities.color import Color
from .api import Api
from .interface import HueInterface


class HueLight(HueInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name, "lights", "state")
        self._capability: Optional[Capability] = None

    @property
    def capability(self) -> Capability:
        if not self._capability:
            self._capability = self._get_capability()
        return self._capability

    def _get_capability(self) -> Capability:
        data = self._get_data()
        if data and "type" in data:
            capability = Capabilities.find(data["type"])
            if capability:
                return capability

        return Capabilities.none.value

    def _get_data(self) -> Union[Dict[str, Any], None]:
        return Api.get(f"/lights/{self.id}")

    @staticmethod
    def find(name: str) -> Union[HueLight, None]:
        """Search for a light in the hue bridge"""
        hue_light = HueLight(name)
        if hue_light.id != HueInterface.INVALID_ID:
            return hue_light
        return None

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        if not self.capability.dim:
            return
        super().dim(value, transition_time)

    def color(self, color: Color, transition_time: float = 1) -> None:
        if not self.capability.color:
            return
        super().color(color, transition_time)


class Capability:
    def __init__(self, type: str, dim: bool, color: bool) -> None:
        self.type = type
        self.dim = dim
        self.color = color


class Capabilities(Enum):
    none = Capability("N/A", dim=True, color=True)
    socket = Capability("On/Off plug-in unit", dim=False, color=False)
    dimmable = Capability("Dimmable light", dim=True, color=False)
    color = Capability("Color light", dim=True, color=True)

    @staticmethod
    def find(type: str) -> Union[Capability, None]:
        for capability in Capabilities:
            if isinstance(capability.value, Capability):
                if capability.value.type == type:
                    return capability.value
