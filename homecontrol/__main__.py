from .tradfri_gateway import Lights, Groups, TradfriGateway
from .network import Network
from .weather import Weather
from .controller import Controller
from .socket_server import SocketServer
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

# Disable logging from apscheduler
logging.getLogger('apscheduler').setLevel(logging.WARNING)
log_level = logging.getLogger(__name__).getEffectiveLevel()

# Initial update
if log_level != logging.DEBUG:
    Weather.update()
Lights.update()
Groups.update()
Network.update()


# Schedule stuff
scheduler = BlockingScheduler()

# Update information
scheduler.add_job(Weather.update, 'cron', hour='*', minute=3)
scheduler.add_job(Lights.update, 'interval', minutes=1)
scheduler.add_job(Groups.update, 'interval', minutes=1)
scheduler.add_job(Network.update, 'interval', seconds=5)

# Schedule events/commands
scheduler.add_job(Controller.update_all, 'interval', seconds=5)

# Start the socket interface
scheduler.add_job(SocketServer.run)
# scheduler.add_job(SocketServer.test)

scheduler.start()
