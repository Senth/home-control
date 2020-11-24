from .tradfri.tradfri_gateway import TradfriGateway
from .network import Network
from .weather import Weather
from .controller import Controller
from .socket_server import SocketServer
from apscheduler.schedulers.blocking import BlockingScheduler


def main():
    # Initial update
    Weather.update()
    TradfriGateway.update()
    Network.update()

    # Schedule stuff
    scheduler = BlockingScheduler()

    # Update information
    scheduler.add_job(Weather.update, "cron", hour="*", minute=3)
    scheduler.add_job(TradfriGateway.update, "interval", minutes=1)
    scheduler.add_job(Network.update, "interval", seconds=5)

    # Schedule events/commands
    scheduler.add_job(Controller.update_all, "interval", seconds=5)

    # Start the socket interface
    scheduler.add_job(SocketServer.run)

    scheduler.start()


if __name__ == "__main__":
    main()
