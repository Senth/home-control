from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .api import Api


class Sensor:
    sensors: List[Sensor] = []

    def __init__(self, id: int, update_interval_seconds: float, log: bool) -> None:
        self.id = id
        self._update_interval_seconds = update_interval_seconds
        self.log = log
        self.last_update = 0
        Sensor.sensors.append(self)

    @staticmethod
    def update_all() -> None:
        for sensor in Sensor.sensors:
            sensor.update()

    def update(self) -> None:
        if self._should_update():
            data = self._get_data()
            if data:
                self.on_update(data)

    def on_update(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError("on_update() should be implemented in the derived class")

    def _should_update(self) -> bool:
        return self._elapsed_time_since_last_update() >= self._update_interval_seconds

    def _elapsed_time_since_last_update(self) -> float:
        return time.time() - self.last_update

    def _get_data(self) -> Optional[Dict[str, Any]]:
        data = Api.get(f"/sensors/{self.id}")
        if data and "state" in data:
            return data
        return None
