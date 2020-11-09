from .config import config
from datetime import datetime

logger = config.logger


class Stats:
    @staticmethod
    def log(category, value):
        if config.stats_file:
            # Calculate date
            currentDate = datetime.today().strftime("%Y-%m-%d %H:%M")
            output = "{},{},{},\n".format(currentDate, category, value)
            try:
                with open(config.stats_file, "a") as file:
                    file.write(output)
            except Exception:
                logger.warning("Couldn't log stat", exc_info=True)
