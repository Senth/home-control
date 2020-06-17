from subprocess import Popen, DEVNULL
from .config import SCHEDULE_RUN_FILE


def run_scheduled_actions():
    Popen(SCHEDULE_RUN_FILE, stderr=DEVNULL, stdout=DEVNULL)
