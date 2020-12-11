from .tradfri.tradfri_gateway import TradfriGateway
from .network import Network
from .weather import Weather
from .controller import Controller
from .webapi import flask_api
from apscheduler.schedulers.background import BackgroundScheduler


def main():
    # Initial update
    Weather.update()
    TradfriGateway.update()
    Network.update()

    # Schedule stuff
    scheduler = BackgroundScheduler()

    # Update information
    scheduler.add_job(Weather.update, "cron", hour="*", minute=3)
    scheduler.add_job(TradfriGateway.update, "interval", minutes=1)
    scheduler.add_job(Network.update, "interval", seconds=5)

    # Schedule events/commands
    scheduler.add_job(Controller.update_all, "interval", seconds=5)

    scheduler.start()

    # Web API
    flask_api.run_api()


if __name__ == "__main__":
    main()
