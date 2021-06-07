import sqlite3
import time
from typing import Union

from ..config import config

logger = config.logger


class Stats:
    db: Union[sqlite3.Connection, None] = None

    @staticmethod
    def log(category, value):
        # Init
        if not Stats.db:
            Stats.init()

        if config.stats_file:
            try:
                cursor = Stats.db.execute(
                    "INSERT INTO stat (timestamp, type, value) VALUES(?, ?, ?)",
                    (
                        int(time.time()),
                        category,
                        value,
                    ),
                )
                cursor.close()
                Stats.db.commit()
            except sqlite3.Error:
                logger.warning("Couldn't log stat", exc_info=True)

    @staticmethod
    def init():
        if config.stats_file:
            Stats.db = sqlite3.connect(str(config.stats_file))
            cursor = Stats.db.cursor()

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS stat (timestamp INTEGER NOT NULL, type TEXT NOT NULL, value TEXT NOT NULL)"
            )
            cursor.close()
            Stats.db.commit()
