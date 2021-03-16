from typing import Any, Dict, Union
from ..interface import Interface
from ..moods import Mood
from .api import Api


class HueInterface(Interface):
    def __init__(self, id: int, name: str, type: str, action: str) -> None:
        super().__init__(name)
        self.id = id
        self.type = type
        self.action = action

    def _get_data(self) -> Union[Dict[str, Any], None]:
        return Api.get(f"/{self.type}/{self.id}")

    def _get_state(self) -> Union[Dict[str, Any], None]:
        data = self._get_data()
        if data and self.action in data:
            state = data[self.action]
            if isinstance(state, dict):
                return state

    def turn_on(self) -> None:
        self._put({"on": True})

    def turn_off(self) -> None:
        self._put({"on": False})

    def toggle(self) -> None:
        new_state = not self.is_on()
        self._put({"on": new_state})

    def is_on(self) -> bool:
        state = self._get_state()
        if state and "on" in state:
            return state["on"]

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
        pass
        # TODO color_xy()

    def mood(self, mood: Mood) -> None:
        self.dim(mood.brightness)
        self.color_xy(mood.x, mood.y)

    def _put(self, body: Dict[str, Any]) -> None:
        Api.put(f"/{self.type}/{self.id}/{self.action}", body)
