import logging
import logging.handlers
from typing import Any, Optional

from tealprint import TealLevel, TealPrint

_app_name = "home-control"


class Config:
    def __init__(self):
        self.general: General = General()
        self.unifi: Unifi = Unifi()
        self.location: Location = Location()
        self.hue: Hue = Hue()
        self.app_name: str = _app_name

    def add_args_settings(self, args: Any) -> None:
        """Set additional configuration from script arguments"""
        if args.debug:
            self.general.log_level = TealLevel.debug
            TealPrint.level = TealLevel.debug

        elif args.verbose:
            self.general.log_level = TealLevel.verbose
            TealPrint.level = TealLevel.verbose

        self._update_external_loggers()

    def _update_external_loggers(self) -> None:
        ap_log_level = logging.WARNING

        if self.general.log_level == TealLevel.debug:
            ap_log_level = logging.INFO

        # Set apscheduler log level
        ap_logger = logging.getLogger("apscheduler")
        ap_logger.setLevel(ap_log_level)


class General:
    def __init__(self) -> None:
        self.port: int = 5001
        self.log_level: TealLevel = TealLevel.info
        self.stats_file: Optional[str] = None


class Hue:
    def __init__(self):
        self.host: str = ""
        self.username: str = ""


class Location:
    def __init__(self):
        self.long: str = ""
        self.lat: str = ""

    def weather_url(self):
        return f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{self.long}/lat/{self.lat}/data.json"


class Unifi:
    def __init__(self):
        self.username: str = ""
        self.password: str = ""
        self.host: str = ""
        self.port: int = 8444
        self.site_id: str = "default"
        self.guest_inactive_time: int = 300


config = Config()
