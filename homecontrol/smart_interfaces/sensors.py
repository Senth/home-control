from .hue.light_sensor import LightSensor


class Sensors:
    light_sensor = LightSensor(3, "Daylight Sensor", True)
