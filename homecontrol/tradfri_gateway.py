from time import sleep

from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.group import Group
from pytradfri.api.libcoap_api import APIFactory, _LOGGER
from pytradfri.error import RequestTimeout
from .config import HOST, IDENTITY, KEY
import logging


logger = logging.getLogger(__name__)

api_factory = APIFactory(host=HOST, psk_id=IDENTITY, psk=KEY)

api = api_factory.request
gateway = Gateway()


def try_several_times(command, recursive=False, max_tries=10):
    try_count = 1
    while True:
        try:
            response = api(command)
            if recursive:
                response = api(response)
            return response
        except RequestTimeout:
            try_count += 1
            logger.info(
                'try_several_times() Failed to run command, trying again... (try #{})'.format(try_count))
            sleep(1)

            if try_count > max_tries:
                TradfriGateway.reboot()
                raise


class Lights:
    window = "Window lights"
    ball = "Ball lights"
    ceiling = "Ceiling light"
    sun_lamp = "Sun lamp"
    led_strip = "LED strip"
    monitor = "Monitor lights"
    billy = "Billy lights"
    bamboo = "Bamboo lamp"
    hall = "Hall light"
    ac = "AC"
    cylinder = "Cylinder lamp"
    micro = "Micro lights"
    emma_star = "Stjärnan lampa"
    emma_billy = "Bokhylla lampa"
    emma_salt = "Salt lampa"
    emma_slinga = "Ljusslinga lampa"

    devices = []

    @staticmethod
    def update():
        """Bind all lights to the correct pytradfri light"""
        Lights.devices = try_several_times(
            gateway.get_devices(), recursive=True)

        for device in Lights.devices:
            if Lights.window == device.name or (isinstance(Lights.window, Device) and Lights.window.has_socket_control and Lights.window.id == device.id):
                Lights.window = device
            elif Lights.ball == device.name or (isinstance(Lights.ball, Device) and Lights.ball.has_socket_control and Lights.ball.id == device.id):
                Lights.ball = device
            elif Lights.ceiling == device.name or (isinstance(Lights.ceiling, Device) and Lights.ceiling.has_light_control and Lights.ceiling.id == device.id):
                Lights.ceiling = device
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
            elif Lights.cylinder == device.name or (isinstance(Lights.cylinder, Device) and Lights.cylinder.has_light_control and Lights.cylinder.id == device.id):
                Lights.cylinder = device
            elif Lights.micro == device.name or (isinstance(Lights.micro, Device) and Lights.micro.has_socket_control and Lights.micro.id == device.id):
                Lights.micro = device
            elif Lights.emma_star == device.name or (isinstance(Lights.emma_star, Device) and Lights.emma_star.has_socket_control and Lights.emma_star.id == device.id):
                Lights.emma_star = device
            elif Lights.emma_billy == device.name or (isinstance(Lights.emma_billy, Device) and Lights.emma_billy.has_socket_control and Lights.emma_billy.id == device.id):
                Lights.emma_billy = device
            elif Lights.emma_salt == device.name or (isinstance(Lights.emma_salt, Device) and Lights.emma_salt.has_socket_control and Lights.emma_salt.id == device.id):
                Lights.emma_salt = device
            elif Lights.emma_slinga == device.name or (isinstance(Lights.emma_slinga, Device) and Lights.emma_slinga.has_socket_control and Lights.emma_slinga.id == device.id):
                Lights.emma_slinga = device
            elif Lights.ac == device.name or (isinstance(Lights.ac, Device) and Lights.ac.has_socket_control and Lights.ac.id == device.id):
                Lights.ac = device
            elif device.has_light_control or device.has_socket_control:
                logger.warning("Didn't update/bind device: " + str(device))

    @staticmethod
    def find_light(name):
        for device in Lights.devices:
            if device.name.lower() == name.lower():
                return device


class Groups:
    matteus = "Matteus"
    living_room = "Vardagsrum"
    cozy = "Vardagsrum (mys)"
    bamboo = "Bamboo"
    emma = "Emma"
    hall = "Hallen"
    matteus_led_strip = "Matteus (LED strip)"
    sun = "Sun"
    kitchen = "Köket"

    groups = []
    moods = {}

    @staticmethod
    def update():
        Groups.groups = try_several_times(gateway.get_groups(), recursive=True)

        for group in Groups.groups:
            Groups.moods[group.id] = try_several_times(
                group.moods(), recursive=True)

            if Groups.matteus == group.name or (isinstance(Groups.matteus, Group) and Groups.matteus.id == group.id):
                Groups.matteus = group
            elif Groups.living_room == group.name or (isinstance(Groups.living_room, Group) and Groups.living_room.id == group.id):
                Groups.living_room = group
            elif Groups.cozy == group.name or (isinstance(Groups.cozy, Group) and Groups.cozy.id == group.id):
                Groups.cozy = group
            elif Groups.bamboo == group.name or (isinstance(Groups.bamboo, Group) and Groups.bamboo.id == group.id):
                Groups.bamboo = group
            elif Groups.emma == group.name or (isinstance(Groups.emma, Group) and Groups.emma.id == group.id):
                Groups.emma = group
            elif Groups.hall == group.name or (isinstance(Groups.hall, Group) and Groups.hall.id == group.id):
                Groups.hall = group
            elif Groups.matteus_led_strip == group.name or (isinstance(Groups.matteus_led_strip, Group) and Groups.matteus_led_strip.id == group.id):
                Groups.matteus_led_strip = group
            elif Groups.sun == group.name or (isinstance(Groups.sun, Group) and Groups.sun.id == group.id):
                Groups.sun = group
            elif Groups.kitchen == group.name or (isinstance(Groups.kitchen, Group) and Groups.kitchen.id == group.id):
                Groups.kitchen = group
            else:
                logger.warning("Didn't update/bind group: " + str(group))

    @staticmethod
    def find_group(name):
        for group in Groups.groups:
            if group.name.lower() == name.lower():
                return group

    @staticmethod
    def find_mood(group, mood_name=None, mood_id=None):
        moods = Groups.moods[group.id]

        if mood_id:
            for mood in moods:
                if mood_id == mood.id:
                    return mood

        if mood_name:
            for mood in moods:
                if mood_name.lower() == mood.name.lower():
                    return mood

    @staticmethod
    def set_mood(group, mood_name=None, mood_id=None):
        # Get mood id
        if mood_name and not mood_id:
            mood = Groups.find_mood(group, mood_name=mood_name)

            if mood:
                mood_id = mood.id
            else:
                logger.warning(
                    "Groups.set_mood() No mood found with the name {}.".format(mood_name))

        if mood_id:
            logger.debug("Groups.set_mood() Setting mood to {} in {}.".format(
                mood_name, group.name))
            try_several_times(group.activate_mood(mood_id))


class TradfriGateway:
    @staticmethod
    def reboot():
        """Reboot the gateway"""
        try_several_times(gateway.reboot())

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
            try_several_times(light_or_group.light_control.set_state(1))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            try_several_times(light_or_group.socket_control.set_state(1))
        elif isinstance(light_or_group, Group):
            try_several_times(light_or_group.set_state(1))

    @staticmethod
    def turn_off(light_or_group):
        """ Turn off a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        """

        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.turn_off(i)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            try_several_times(light_or_group.light_control.set_state(0))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            try_several_times(light_or_group.socket_control.set_state(0))
        elif isinstance(light_or_group, Group):
            try_several_times(light_or_group.set_state(0))

    @staticmethod
    def isOn(light_or_group):
        """Check if a light or group is turned on or not"""
        if isinstance(light_or_group, Device) and light_or_group.has_light_control:
            return light_or_group.light_control.lights[0].state
        if isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            return light_or_group.socket_control.sockets[0].state
        if isinstance(light_or_group, Group):
            return light_or_group.state

    @staticmethod
    def toggle(light_or_group):
        """ Toggle a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        """

        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.toggle(i)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            new_state = not bool(light_or_group.light_control.lights[0].state)
            try_several_times(
                light_or_group.light_control.set_state(new_state))
        elif isinstance(light_or_group, Device) and light_or_group.has_socket_control:
            new_state = not bool(
                light_or_group.socket_control.sockets[0].state)
            try_several_times(
                light_or_group.socket_control.set_state(new_state))
        elif isinstance(light_or_group, Group):
            new_state = not bool(light_or_group.state)
            try_several_times(light_or_group.set_state(new_state))

    @staticmethod
    def dim(light_or_group, value, transition_time=10):
        """ Dim a light or group
        :param light_or_group: Can be either a light or group. Can be a list of lights and groups
        :param value the dim value between 0 and 254
        :param transition_time time in 100ms for it to transition
        """
        if isinstance(light_or_group, Device):
            logger.debug("TradfriGateway.dim() Dim{} to {} with transition time {}.".
                         format(light_or_group.name, value, transition_time))

        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.dim(i, value, transition_time)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            if light_or_group.light_control.can_set_dimmer:
                try_several_times(light_or_group.light_control.set_dimmer(
                    value, transition_time=transition_time))
        elif isinstance(light_or_group, Group):
            try_several_times(light_or_group.set_dimmer(
                value, transition_time=transition_time))

    @staticmethod
    def color(light_or_group, x, y, transition_time=10):
        """Set the color of a light or group
        :param light_or_group Can be either a light or group or a list containing lights and groups
        :param x x-value of the color
        :param y y-value of the color
        :param transition_time time in 100ms for it to transition, default 10 = 1 second
        """
        if isinstance(light_or_group, list):
            for i in light_or_group:
                TradfriGateway.color(i, x, y, transition_time)
        elif isinstance(light_or_group, Device) and light_or_group.has_light_control:
            if light_or_group.light_control.can_set_xy:
                try_several_times(light_or_group.light_control.set_xy_color(
                    x, y, transition_time=transition_time))
        elif isinstance(light_or_group, Group):
            try_several_times(light_or_group.set_xy_color(
                x, y, transition_time=transition_time))
