from .config import config
from .controller import Controller
from .data.network import Network
from .smart_interfaces.hue.sensor import Sensor
from .utils.arg_parser import parse_args
from .utils.config_gateway import ConfigGateway
from .utils.thread import start_thread
from .webapi import flask_api


def main():
    # Get configuration
    config_gateway = ConfigGateway()
    config_gateway.check_config_exists()
    config_gateway.read()
    config.general = config_gateway.get_general()
    config.hue = config_gateway.get_hue()
    config.location = config_gateway.get_location()
    config.unifi = config_gateway.get_unifi()
    config.add_args_settings(parse_args())

    # Start home-control
    start_thread(Sensor.update_all, seconds_between_calls=5)
    start_thread(Network.update, seconds_between_calls=5)
    start_thread(Controller.update_all, seconds_between_calls=1, delay=10)

    # Run Web API
    flask_api.run_api()


if __name__ == "__main__":
    main()
