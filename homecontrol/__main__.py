from .tradfri_gateway import Lights, Groups, TradfriGateway
from .networkdevice import NetworkDevices
from .weather import Weather
from .controller import Controller
from apscheduler.schedulers.blocking import BlockingScheduler


# Initial update
Weather.update()
Lights.update()
Groups.update()
NetworkDevices.update()


# Schedule stuff
scheduler = BlockingScheduler()

# Update information
scheduler.add_job(Weather.update, 'cron', hour='*', minute=2)
scheduler.add_job(Lights.update, 'interval', minutes=5)
scheduler.add_job(Groups.update, 'interval', minutes=5)
scheduler.add_job(NetworkDevices.update, 'interval', seconds=15)

# Schedule events/commands
scheduler.add_job(Controller.update_all, 'interval', seconds=5)

# from .sun import Sun
# Sun.update()
# Sun.is_bright()


scheduler.start()
