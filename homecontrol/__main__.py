from .tradfri.tradfri_gateway import TradfriGateway
from .tradfri.motion_sensor import MotionSensor
from .network import Network
from .weather import Weather
from .controller import Controller
from .webapi import flask_api
from .thread import start_thread
from apscheduler.schedulers.background import BackgroundScheduler


def main():
    # Initial update
    Weather.update()

    # Schedule stuff
    scheduler = BackgroundScheduler()

    # Update information
    scheduler.add_job(Weather.update, "cron", hour="*", minute=3)
    scheduler.start()

    start_thread(Network.update, seconds_between_calls=5)
    start_thread(TradfriGateway.update, seconds_between_calls=60)
    start_thread(Controller.update_all, seconds_between_calls=1, delay=10)
    # start_thread(MotionSensor.update_all, seconds_between_calls=10) NOTE doesn't work yet

    # Web API
    flask_api.run_api()


if __name__ == "__main__":
    main()
