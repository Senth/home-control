from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.api.libcoap_api import APIFactory, _LOGGER
from .config import HOST, IDENTITY, KEY

import logging


_LOGGER.setLevel(logging.DEBUG)
print(HOST)
print(IDENTITY)

api_factory = APIFactory(host=HOST, psk_id=IDENTITY, psk=KEY)

api = api_factory.request
gateway = Gateway()


class Lights:
    WINDOW = "Window lights"
    BALL = "Ball lights"
    CEILING = "Ceiling light"
    EMMA = "Emma"
    LED_STRIP = "LED strip"
    MONITOR = "Monitor lights"
    DARK_SOULS = "Dark Souls lights"
    BAMBOO = "Bamboo lamp"
    SUN = "Sun lamp"

    """Bind all lights to the correct pytradfri light"""
    @staticmethod
    def update_lights():
        command = api(gateway.get_devices())
        devices = api(command)

        for device in devices:
            if Lights.WINDOW == device.name or (isinstance(Lights.WINDOW, Device) and Lights.WINDOW.has_socket_control and Lights.WINDOW.id == device.id):
                Lights.WINDOW = device
            elif Lights.BALL == device.name or (isinstance(Lights.BALL, Device) and Lights.BALL.has_socket_control and Lights.BALL.id == device.id):
                Lights.BALL = device
            elif Lights.CEILING == device.name or (isinstance(Lights.CEILING, Device) and Lights.CEILING.has_light_control and Lights.CEILING.id == device.id):
                Lights.CEILING = device
            elif Lights.EMMA == device.name or (isinstance(Lights.EMMA, Device) and Lights.EMMA.has_socket_control and Lights.EMMA.id == device.id):
                Lights.EMMA = device
            elif Lights.LED_STRIP == device.name or (isinstance(Lights.LED_STRIP, Device) and Lights.LED_STRIP.has_socket_control and Lights.LED_STRIP.id == device.id):
                Lights.LED_STRIP = device
            elif Lights.MONITOR == device.name or (isinstance(Lights.MONITOR, Device) and Lights.MONITOR.has_socket_control and Lights.MONITOR.id == device.id):
                Lights.MONITOR = device
            elif Lights.DARK_SOULS == device.name or (isinstance(Lights.DARK_SOULS, Device) and Lights.DARK_SOULS.has_socket_control and Lights.DARK_SOULS.id == device.id):
                Lights.DARK_SOULS = device
            elif Lights.BAMBOO == device.name or (isinstance(Lights.BAMBOO, Device) and Lights.BAMBOO.has_light_control and Lights.BAMBOO.id == device.id):
                Lights.BAMBOO = device
            elif Lights.SUN == device.name or (isinstance(Lights.SUN, Device) and Lights.SUN.has_socket_control and Lights.SUN.id == device.id):
                Lights.SUN = device
            elif device.has_light_control or device.has_socket_control:
                print("Didn't update/bind device: " + str(device))

class Groups:
    MATTEUS = "Matteus"
    COZY = "Vardagsrum (mys)"

# 
# class TradfriGateway:
#     def turn_on(light_or_set):
#         pass
# 
#     def turn_off(light_or_set):
#         pass
# 
#     def toggle(light_or_set):
#         pass
# 
