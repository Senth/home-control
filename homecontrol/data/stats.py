from datetime import datetime

from ..config import config

logger = config.logger


class Stats:
    @staticmethod
    def log(category, value):
        if config.stats_file:
            # Calculate date
            currentDate = datetime.today().strftime("%Y-%m-%d %H:%M")
            output = f"{currentDate},{category},{value}\n"
            try:
                with open(config.stats_file, "a+") as file:
                    file.write(output)
            except:
                logger.warning("Couldn't log stat", exc_info=True)
