import sqlite3
import time

from tealprint import TealPrint

from ..config import config


class Stats:
    @staticmethod
    def log(category, value):
        if config.general.stats_file:
            db = Stats.init()
            try:
                cursor = db.execute(
                    "INSERT INTO stat (timestamp, type, value) VALUES(?, ?, ?)",
                    (
                        int(time.time()),
                        category,
                        value,
                    ),
                )
                cursor.close()
                db.commit()
            except sqlite3.Error:
                TealPrint.error("❗ Couldn't log stat", print_exception=True)
            db.close()

    @staticmethod
    def init() -> sqlite3.Connection:
        db = sqlite3.connect(str(config.general.stats_file))
        cursor = db.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS stat (timestamp INTEGER NOT NULL, type TEXT NOT NULL, value TEXT NOT NULL)"
        )
        cursor.close()
        db.commit()
        return db
