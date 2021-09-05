from .hue.light_sensor import LightLevels, LightSensor


class Sensors:
    light_sensor = LightSensor(3, "Daylight Sensor", True)
