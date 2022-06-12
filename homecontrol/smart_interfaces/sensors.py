from .hue.light_sensor import LightSensor


class Sensors:
    livingroom_light = LightSensor(3, "Livingroom Daylight Sensor", 6000, 11000, 15000, 18000, log=True)
    kitchen_light = LightSensor(10, "Kitchen Daylight Sensor", 7000, 12000, 16000, 20000, log=True)
