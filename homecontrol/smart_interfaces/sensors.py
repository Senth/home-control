from enum import Enum

from .hue.light_sensor import LightSensor


class Sensors(Enum):
    light_sensor = LightSensor(3, True)
