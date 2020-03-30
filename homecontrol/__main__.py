from .tradfri_gateway import Lights, Groups, TradfriGateway
from .network import Network
from .weather import Weather
from .controller import Controller
from .schedule_runner import run_scheduled_actions
from .socket_server import SocketServer
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

# Disable logging from apscheduler
logging.getLogger('apscheduler').setLevel(logging.WARNING);

# Initial update
Weather.update()
Lights.update()
Groups.update()
Network.update()


# Schedule stuff
scheduler = BlockingScheduler()

# Update information
scheduler.add_job(Weather.update, 'cron', hour='*', minute=42)
# scheduler.add_job(Lights.update, 'interval', minutes=50)
# scheduler.add_job(Groups.update, 'interval', minutes=50)
scheduler.add_job(Network.update, 'interval', seconds=5)

# Schedule events/commands
scheduler.add_job(Controller.update_all, 'interval', seconds=5)

# Schedule checking of scheduled actions
scheduler.add_job(run_scheduled_actions, 'interval', seconds=5)

# Start the socket interface
scheduler.add_job(SocketServer.run)
# scheduler.add_job(SocketServer.test)

scheduler.start()
