from .config import STATS_FILE
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Stats:
    @staticmethod
    def log(category, value):
        # Calculate date
        currentDate = datetime.today().strftime('%Y-%m-%d %H:%M')
        output = '{},{},{},\n'.format(currentDate, category, value)
        try:
            with open(STATS_FILE, 'a') as file:
                file.write(output)
        except Exception:
            logger.warning("Couldn't log stat", exc_info=True)
