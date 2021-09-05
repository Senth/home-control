from apscheduler.schedulers.background import BackgroundScheduler

from .controller import Controller
from .data.network import Network
from .data.weather import Weather
from .smart_interfaces.hue.sensor import Sensor
from .utils.thread import start_thread
from .webapi import flask_api


def main():
    start_thread(Sensor.update_all, seconds_between_calls=5)
    start_thread(Network.update, seconds_between_calls=5)
    start_thread(Controller.update_all, seconds_between_calls=1, delay=10)

    # Web API
    flask_api.run_api()


if __name__ == "__main__":
    main()
