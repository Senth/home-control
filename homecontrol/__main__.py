from .tradfri_gateway import Lights, Groups, TradfriGateway
from .networkdevice import NetworkDevices
from .weather import Weather
from .controller import Controller
from .schedule_runner import run_scheduled_actions
from apscheduler.schedulers.blocking import BlockingScheduler


# Initial update
Weather.update()
Lights.update()
Groups.update()
NetworkDevices.update()


# Schedule stuff
scheduler = BlockingScheduler()

# Update information
scheduler.add_job(Weather.update, 'cron', hour='*', minute=42)
scheduler.add_job(Lights.update, 'interval', minutes=5)
scheduler.add_job(Groups.update, 'interval', minutes=5)
scheduler.add_job(NetworkDevices.update, 'interval', seconds=15)

# Schedule events/commands
scheduler.add_job(Controller.update_all, 'interval', seconds=5)

# Schedule checking of scheduled actions
scheduler.add_job(run_scheduled_actions, 'interval', seconds=5)


scheduler.start()
