from __future__ import annotations
from typing import Any, Dict, Union
from ..interface import Interface
from ..moods import Mood
from .api import Api


class HueLight(Interface):
    def __init__(self, id: int, name: str) -> None:
        super().__init__(name)
        self.id = id

    @staticmethod
    def find(name: str) -> Union[HueLight, None]:
        """Search for a light in the hue bridge"""
        name = name.lower()
        lights = Api.get(f"/lights")

        if lights:
            for id, data in lights.items():
                if "name" in data and str(data["name"]).lower() == name:
                    return HueLight(int(id), str(data["name"]))

    def turn_on(self) -> None:
        self._put({"on": True})

    def turn_off(self) -> None:
        self._put({"on": False})

    def toggle(self) -> None:
        new_state = not self.is_on()
        self._put({"on": new_state})

    def is_on(self) -> bool:
        state = Api.get(f"/lights/{self.id}")
        if state:
            return state["state"]["on"]
        return False

    def dim(self, value: Union[float, int], transition_time: float = 1) -> None:
        normalized_value = Interface.normalize_dim(value)
        normalized_time = Interface.normalize_transition_time(transition_time)
        self._put(
            {
                "on": True,
                "bri": normalized_value,
                "transition_time": normalized_time,
            }
        )

    def color_xy(self, x: int, y: int, transition_time: float = 1) -> None:
        # TODO color_xy()
        pass

    def mood(self, mood: Mood) -> None:
        # TODO mood()
        pass

    def _put(self, body: Dict[str, Any]) -> None:
        Api.put(f"/lights/{self.id}/state", body)
