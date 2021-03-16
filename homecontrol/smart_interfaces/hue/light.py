from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Union
from ..moods import Mood
from .interface import HueInterface
from .api import Api


class HueLight(HueInterface):
    def __init__(self, id: int, name: str) -> None:
        super().__init__(id, name, "lights", "state")
        self.capability = self._get_capability()

    def _get_capability(self) -> Capability:
        data = self._get_data()
        if data and "type" in data:
            capability = Capabilities.find(data["type"])
            if capability:
                return capability

        return Capabilities.none.value

    def _get_data(self) -> Union[Dict[str, Any], None]:
        return Api.get(f"/lights/{self.id}")

    def _get_state(self) -> Union[Dict[str, Any], None]:
        data = self._get_data()
        if data and "state" in data:
            state = data["state"]
            if isinstance(state, dict):
                return state

    @staticmethod
    def find(name: str) -> Union[HueLight, None]:
        """Search for a light in the hue bridge"""
        name = name.lower()
        lights = Api.get(f"/lights")

        if lights:
            for id, data in lights.items():
                if "name" in data and str(data["name"]).lower() == name:
                    return HueLight(int(id), str(data["name"]))

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        if not self.capability.dim:
            return
        super().dim(value, transition_time)

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        if not self.capability.color:
            return
        super().color_xy(x, y, transition_time)

    def mood(self, mood: Mood) -> None:
        self.dim(mood.brightness)
        self.color_xy(mood.x, mood.y)


class Capability:
    def __init__(self, type: str, dim: bool, color: bool) -> None:
        self.type = type
        self.dim = dim
        self.color = color


class Capabilities(Enum):
    none = Capability("N/A", dim=True, color=True)
    socket = Capability("On/Off plug-in unit", dim=False, color=False)
    dimmable = Capability("Dimmable light", dim=True, color=False)

    @staticmethod
    def find(type: str) -> Union[Capability, None]:
        for capability in Capabilities:
            if isinstance(capability.value, Capability):
                if capability.value.type == type:
                    return capability.value
