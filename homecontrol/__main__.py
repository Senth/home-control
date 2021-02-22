from .data.network import Network
from .data.weather import Weather
from .controller import Controller
from .webapi import flask_api
from .utils.thread import start_thread
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
    start_thread(Controller.update_all, seconds_between_calls=1, delay=10)

    # Web API
    flask_api.run_api()


if __name__ == "__main__":
    main()
