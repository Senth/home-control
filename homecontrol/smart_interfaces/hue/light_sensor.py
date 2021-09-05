from typing import Any, Dict

from ...data.stats import Stats
from .sensor import Sensor


class LightSensor(Sensor):
    def __init__(self, id: int, log: bool = False) -> None:
        super().__init__(id, 60 * 5, log)
        self.name: str = ""
        self.light_level: int = 0

    def on_update(self, data: Dict[str, Any]) -> None:
        self.name = data["name"]
        self.light_level = data["state"]["lightlevel"]

        if self.log:
            Stats.log("light_level", self.light_level)
