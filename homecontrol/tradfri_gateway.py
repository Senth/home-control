from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.group import Group
from pytradfri.api.libcoap_api import APIFactory, _LOGGER
from .config import HOST, IDENTITY, KEY
import logging


logger = logging.getLogger(__name__)

api_factory = APIFactory(host=HOST, psk_id=IDENTITY, psk=KEY)

api = api_factory.request
gateway = Gateway()


class Lights:
    window = "Window lights"
    ball = "Ball lights"
    ceiling = "Ceiling light"
    emma = "Emma"
    sun_lamp = "Sun lamp"
    led_strip = "LED strip"
    monitor = "Monitor lights"
    billy = "Billy lights"
    bamboo = "Bamboo lamp"
    hall = "Hall light"
    cylinder = "Cylinder lamp"
    micro = "Micro lights"

    devices = []

    """Bind all lights to the correct pytradfri light"""
    @staticmethod
    def update():
        command = api(gateway.get_devices())
        Lights.devices = api(command)

        for device in Lights.devices:
            if Lights.window == device.name or (isinstance(Lights.window, Device) and Lights.window.has_socket_control and Lights.window.id == device.id):
                Lights.window = device
            elif Lights.ball == device.name or (isinstance(Lights.ball, Device) and Lights.ball.has_socket_control and Lights.ball.id == device.id):
                Lights.ball = device
            elif Lights.ceiling == device.name or (isinstance(Lights.ceiling, Device) and Lights.ceiling.has_light_control and Lights.ceiling.id == device.id):
                Lights.ceiling = device
            elif Lights.emma == device.name or (isinstance(Lights.emma, Device) and Lights.emma.has_socket_control and Lights.emma.id == device.id):
                Lights.emma = device
            elif Lights.sun_lamp == device.name or (isinstance(Lights.sun_lamp, Device) and Lights.sun_lamp.has_socket_control and Lights.sun_lamp.id == device.id):
                Lights.sun_lamp = device
            elif Lights.led_strip == device.name or (isinstance(Lights.led_strip, Device) and Lights.led_strip.has_socket_control and Lights.led_strip.id == device.id):
                Lights.led_strip = device
            elif Lights.monitor == device.name or (isinstance(Lights.monitor, Device) and Lights.monitor.has_socket_control and Lights.monitor.id == device.id):
                Lights.monitor = device
            elif Lights.billy == device.name or (isinstance(Lights.billy, Device) and Lights.billy.has_socket_control and Lights.billy.id == device.id):
                Lights.billy = device
            elif Lights.bamboo == device.name or (isinstance(Lights.bamboo, Device) and Lights.bamboo.has_light_control and Lights.bamboo.id == device.id):
                Lights.bamboo = device
            elif Lights.hall == device.name or (isinstance(Lights.hall, Device) and Lights.hall.has_socket_control and Lights.hall.id == device.id):
                Lights.hall = device
            elif Lights.cylinder == device.name or (isinstance(Lights.cylinder, Device) and Lights.cylinder.has_socket_control and Lights.cylinder.id == device.id):
                Lights.cylinder = device
            elif Lights.micro == device.name or (isinstance(Lights.micro, Device) and Lights.micro.has_socket_control and Lights.micro.id == device.id):
                Lights.micro = device
            elif device.has_light_control or device.has_socket_control:
                logger.warning("Didn't update/bind device: " + str(device))

    @staticmethod
    def find_light(name):
        for device in Lights.devices:
            if device.name.lower() == name.lower():
                return device
        return None


class Groups:
    matteus = "Matteus"
    cozy = "Vardagsrum (mys)"

    groups = []

    @staticmethod
    def update():
        command = api(gateway.get_groups())
        Groups.groups = api(command)

        for group in Groups.groups:
            if Groups.matteus == group.name or (isinstance(Groups.matteus, Group) and Groups.matteus.id == group.id):
                Groups.matteus = group
            elif Groups.cozy == group.name or (isinstance(Groups.cozy, Group) and Groups.cozy.id == group.id):
                Groups.cozy = group
            else:
                logger.warning("Didn't update/bind group: " + str(group))

    @staticmethod
    def find_group(name):
        for group in Groups.groups:
            if group.name.lower() == name.lower():
                return group
        return None


class TradfriGateway:
    @staticmethod
    def turn_on(light_or_group):
        """
        Turn on a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        """
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.turn_on(i)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            api(light_or_group.light_control.set_state(1))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            api(light_or_group.socket_control.set_state(1))
        elif isinstance(light_or_group, Group):
            api(light_or_group.set_state(1))

    @staticmethod
    def turn_off(light_or_group):
        """
        Turn off a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        """
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.turn_off(i)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            api(light_or_group.light_control.set_state(0))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            api(light_or_group.socket_control.set_state(0))
        elif isinstance(light_or_group, Group):
            api(light_or_group.set_state(0))

    @staticmethod
    def toggle(light_or_group):
        """
        Toggle a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        """

        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.toggle(i)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            new_state = not bool(light_or_group.light_control.lights[0].state)
            api(light_or_group.light_control.set_state(new_state))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            new_state = not bool(light_or_group.socket_control.sockets[0].state)
            api(light_or_group.socket_control.set_state(new_state))
        elif isinstance(light_or_group, Group):
            new_state = not bool(light_or_group.state)
            api(light_or_group.set_state(new_state))

    @staticmethod
    def dim(light_or_group, value, transition_time=10):
        """
        Dim a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        :param value the dim value between 0 and 254
        :param transition_time time in 100ms for it to transition
        """
        if isinstance(light_or_group, Device):
            logger.debug("TradfriGateway.dim() Dim {} to {} with transition time {}."
                         .format(light_or_group.name, value, transition_time))

        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.dim(i, value, transition_time)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            if light_or_group.light_control.can_set_dimmer:
                api(light_or_group.light_control.set_dimmer(value, transition_time=transition_time))
        elif isinstance(light_or_group, Group):
            api(light_or_group.set_dimmer(value, transition_time=transition_time))
